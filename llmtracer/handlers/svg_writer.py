#  LLM Tracer
#  Copyright (c) 2023. Andreas Kirsch
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import copy
import os
from dataclasses import dataclass
from enum import Enum

import svgwrite
from svgwrite.base import BaseElement
from svgwrite.elementfactory import factoryelements
from svgwrite.etree import etree
from svgwrite.mixins import Clipping, Presentation, Transform

from llmtracer.trace_builder import TraceBuilder, TraceBuilderEventHandler
from llmtracer.trace_schema import Trace, TraceNode, TraceNodeKind


# solarized colors as HTML hex
# https://ethanschoonover.com/solarized/
class SolarizedColors(str, Enum):
    base03 = "#002b36"
    base02 = "#073642"
    base01 = "#586e75"
    base00 = "#657b83"
    base0 = "#839496"
    base1 = "#93a1a1"
    base2 = "#eee8d5"
    base3 = "#fdf6e3"
    yellow = "#b58900"
    orange = "#cb4b16"
    red = "#dc322f"
    magenta = "#d33682"
    violet = "#6c71c4"
    blue = "#268bd2"
    cyan = "#2aa198"
    green = "#859900"


renderjson = """// Copyright © 2013-2017 David Caldwell <david@porkrind.org>
//
// Permission to use, copy, modify, and/or distribute this software for any
// purpose with or without fee is hereby granted, provided that the above
// copyright notice and this permission notice appear in all copies.
//
// THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
// WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
// SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
// OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
// CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

// Usage
// -----
// The module exports one entry point, the `renderjson()` function. It takes in
// the JSON you want to render as a single argument and returns an HTML
// element.
//
// Options
// -------
// renderjson.set_icons("+", "-")
//   This Allows you to override the disclosure icons.
//
// renderjson.set_show_to_level(level)
//   Pass the number of levels to expand when rendering. The default is 0, which
//   starts with everything collapsed. As a special case, if level is the string
//   "all" then it will start with everything expanded.
//
// renderjson.set_max_string_length(length)
//   Strings will be truncated and made expandable if they are longer than
//   `length`. As a special case, if `length` is the string "none" then
//   there will be no truncation. The default is "none".
//
// renderjson.set_sort_objects(sort_bool)
//   Sort objects by key (default: false)
//
// renderjson.set_replacer(replacer_function)
//   Equivalent of JSON.stringify() `replacer` argument when it's a function
//
// renderjson.set_collapse_msg(collapse_function)
//   Accepts a function (len:number):string => {} where len is the length of the
//   object collapsed.  Function should return the message displayed when a
//   object is collapsed.  The default message is "X items"
//
// renderjson.set_property_list(property_list)
//   Equivalent of JSON.stringify() `replacer` argument when it's an array
//
// Theming
// -------
// The HTML output uses a number of classes so that you can theme it the way
// you'd like:
//     .disclosure    ("⊕", "⊖")
//     .syntax        (",", ":", "{", "}", "[", "]")
//     .string        (includes quotes)
//     .number
//     .boolean
//     .key           (object key)
//     .keyword       ("null", "undefined")
//     .object.syntax ("{", "}")
//     .array.syntax  ("[", "]")

var module, window, define, renderjson = (function() {
  var themetext = function( /* [class, text]+ */ ) {
    /* The arguments are alternating class names and text strings.
     *
     * This function creates a span using the class name and adds the text for each argument pair. It returns the array.
     */
    var spans = [];
    while (arguments.length)
      spans.push(append(span(Array.prototype.shift.call(
          arguments)),
        text(Array.prototype.shift.call(arguments))));
    return spans;
  };

  var append = function( /* el, ... */ ) {
    /* append all arguments to the first one and return the first el. */
    // Flattens arrays.
    var el = Array.prototype.shift.call(arguments);
    for (var a = 0; a < arguments.length; a++)
      if (arguments[a].constructor == Array)
        append.apply(this, [el].concat(arguments[a]));
      else
        el.appendChild(arguments[a]);
    return el;
  };

  var prepend = function(el, child) {
    /* prepend child to el's children */
    el.insertBefore(child, el.firstChild);
    return el;
  }

  var isempty = function(obj, pl) {
    var keys = pl || Object.keys(obj);
    for (var i in keys)
      if (Object.hasOwnProperty.call(obj, keys[i]))
        return false;
    return true;
  }

  var text = function(txt) {
    return document.createTextNode(txt)
  };

  var div = function() {
    return document.createElementNS(
      "http://www.w3.org/1999/xhtml", "div")
  };

  var pre = function(classname) {
    var s = document.createElementNS(
      "http://www.w3.org/1999/xhtml", "pre")
    if (classname) s.className = classname;
    return s;
  };

  var span = function(classname) {
    var s = document.createElementNS(
      "http://www.w3.org/1999/xhtml", "span");
    if (classname) s.className = classname;
    return s;
  };

  var A = function A(txt, classname, callback) {
    var a = document.createElementNS(
      "http://www.w3.org/1999/xhtml", "a");
    if (classname) a.className = classname;
    a.appendChild(text(txt));
    a.href = '#';
    a.onclick = function(e) {
      callback();
      if (e) e.stopPropagation();
      return false;
    };
    return a;
  };

  function _renderjson(json, indent, dont_indent, show_level,
    options) {
    var my_indent = dont_indent ? "" : indent;

    var disclosure = function(open, placeholder, close, type,
      builder) {
      var content;
      var empty = span(type);
      var show = function() {
        if (!content) {
          append(
            empty.parentNode,
            content = prepend(builder(),
              A(
                options.hide, "disclosure",
                function() {
                  content.style.display =
                    "none";
                  empty.style.display =
                    "inline";
                })
            )
          );
        }
        content.style.display = "inline";
        empty.style.display = "none";
      };
      append(empty,
        A(options.show, "disclosure", show),
        themetext(type + " syntax", open),
        A(placeholder, null, show),
        themetext(type + " syntax", close));

      var el = append(span(), text(my_indent.slice(0, -1)),
        empty);
      if (show_level > 0 && type != "string")
        show();
      return el;
    };

    if (json === null) return themetext(null, my_indent, "keyword",
      "null");
    if (json === void 0) return themetext(null, my_indent,
      "keyword", "undefined");

    if (typeof(json) == "string" && json.length > options
      .max_string_length)
      return disclosure('"', json.substr(0, options
          .max_string_length) + " ...", '"', "string",
        function() {
          return append(span("string"), themetext(null,
            my_indent, "string", JSON.stringify(
              json)));
        });

    // Strings: wrap in a <pre>
    if (json.constructor == String) {
        let pre_text = pre(null);
        pre_text.innerHTML = json;
        pre_text.style.whiteSpace = "pre-wrap";
        pre_text.style.display ="inline-flex";
        pre_text.style.overflow = "auto";
        pre_text.style.maxHeight = "400px";
        // add borders for overflow
        pre_text.style.border = "1px solid #ccc";
        // scrollbar-gutter: stable;
        pre_text.style.scrollbarGutter = "stable";
        pre_text.style.margin = "0";

        let as = [
            append(span(null), text(my_indent)),
            append(span("string"), text("\\""), pre_text, text("\\""))
        ];
        return as;
    }

    // Numbers and bools
    if (typeof(json) != "object" || [Number, Boolean, Date]
      .indexOf(json.constructor) >= 0)
      return themetext(null, my_indent, typeof(json), JSON
        .stringify(json));

    if (json.constructor == Array) {
      if (json.length == 0) return themetext(null, my_indent,
        "array syntax", "[]");

      return disclosure("[", options.collapse_msg(json.length),
        "]", "array",
        function() {
          var as = append(span("array"), themetext(
            "array syntax", "[", null, "\\n"));
          for (var i = 0; i < json.length; i++)
            append(as,
              _renderjson(options.replacer.call(json,
                  i, json[i]), indent + "    ",
                false, show_level - 1, options),
              i != json.length - 1 ? themetext(
                "syntax", ",") : [],
              text("\\n"));
          append(as, themetext(null, indent,
            "array syntax", "]"));
          return as;
        });
    }

    // object
    if (isempty(json, options.property_list))
      return themetext(null, my_indent, "object syntax", "{}");

    return disclosure("{", options.collapse_msg(Object.keys(json)
      .length), "}", "object", function() {
      var os = append(span("object"), themetext(
        "object syntax", "{", null, "\\n"));
      for (var k in json) var last = k;
      var keys = options.property_list || Object.keys(
        json);
      if (options.sort_objects)
        keys = keys.sort();
      for (var i in keys) {
        var k = keys[i];
        if (!(k in json)) continue;
        append(os, themetext(null, indent + "    ",
            "key", '"' + k + '"',
            "object syntax", ': '),
          _renderjson(options.replacer.call(json,
              k, json[k]), indent + "    ",
            true, show_level - 1, options),
          k != last ? themetext("syntax", ",") : [],
          text("\\n"));
      }
      append(os, themetext(null, indent, "object syntax",
        "}"));
      return os;
    });
  }

  var renderjson = function renderjson(json) {
    var options = new Object(renderjson.options);
    options.replacer = typeof(options.replacer) == "function" ?
      options.replacer : function(k, v) {
        return v;
      };
    var pre = append(document.createElementNS(
        "http://www.w3.org/1999/xhtml", "pre"),
      _renderjson(json, "", false, options.show_to_level,
        options));
    pre.className = "renderjson";
    return pre;
  }
  renderjson.set_icons = function(show, hide) {
    renderjson.options.show = show;
    renderjson.options.hide = hide;
    return renderjson;
  };
  renderjson.set_show_to_level = function(level) {
    renderjson.options.show_to_level = typeof level ==
      "string" &&
      level.toLowerCase() === "all" ? Number.MAX_VALUE :
      level;
    return renderjson;
  };
  renderjson.set_max_string_length = function(length) {
    renderjson.options.max_string_length = typeof length ==
      "string" &&
      length.toLowerCase() === "none" ? Number.MAX_VALUE :
      length;
    return renderjson;
  };
  renderjson.set_sort_objects = function(sort_bool) {
    renderjson.options.sort_objects = sort_bool;
    return renderjson;
  };
  renderjson.set_replacer = function(replacer) {
    renderjson.options.replacer = replacer;
    return renderjson;
  };
  renderjson.set_collapse_msg = function(collapse_msg) {
    renderjson.options.collapse_msg = collapse_msg;
    return renderjson;
  };
  renderjson.set_property_list = function(prop_list) {
    renderjson.options.property_list = prop_list;
    return renderjson;
  };
  // Backwards compatiblity. Use set_show_to_level() for new code.
  renderjson.set_show_by_default = function(show) {
    renderjson.options.show_to_level = show ? Number.MAX_VALUE :
      0;
    return renderjson;
  };
  renderjson.options = {};
  renderjson.set_icons('⊕', '⊖');
  renderjson.set_show_by_default(false);
  renderjson.set_sort_objects(false);
  renderjson.set_max_string_length("none");
  renderjson.set_replacer(void 0);
  renderjson.set_property_list(void 0);
  renderjson.set_collapse_msg(function(len) {
    return len + " item" + (len == 1 ? "" : "s")
  })
  return renderjson;
})();

if (define) define({
  renderjson: renderjson
})
else(module || {}).exports = (window || {}).renderjson = renderjson;"""


def convert_trace_node_kind_to_color(kind: TraceNodeKind):
    if kind == TraceNodeKind.SCOPE:
        return SolarizedColors.base1
    elif kind == TraceNodeKind.AGENT:
        return SolarizedColors.green
    elif kind == TraceNodeKind.LLM:
        return SolarizedColors.blue
    elif kind == TraceNodeKind.CHAIN:
        return SolarizedColors.cyan
    elif kind == TraceNodeKind.CALL:
        return SolarizedColors.yellow
    elif kind == TraceNodeKind.EVENT:
        return SolarizedColors.orange
    elif kind == TraceNodeKind.TOOL:
        return SolarizedColors.magenta
    else:
        return SolarizedColors.base2


class ForeignObject(BaseElement, Transform, Presentation, Clipping):
    """ForeignObject element.

    The **rect** element defines a rectangle which is axis-aligned with the current
    user coordinate system. Rounded rectangles can be achieved by setting appropriate
    values for attributes **rx** and **ry**.
    """

    elementname = 'foreignObject'
    inner_xml: etree.Element

    def __init__(self, inner_xml: etree.Element, insert=None, size=None, **extra):
        """Initialize a new instance.

        :param inner_xml: XML `ElementTree` of the inner content
        :param 2-tuple insert: insert point (**x**, **y**), left-upper point
        :param 2-tuple size: (**width**, **height**)
        :param extra: additional SVG attributes as keyword-arguments

        """
        super(ForeignObject, self).__init__(**extra)
        if insert is not None:
            self['x'] = insert[0]
            self['y'] = insert[1]
        if size is not None:
            self['width'] = size[0]
            self['height'] = size[1]
        self.inner_xml = inner_xml

    def get_xml(self):
        """Get the XML representation as `ElementTree` object.

        :return: XML `ElementTree` of this object and all its subelements

        """
        xml = etree.Element(self.elementname)
        if self.debug:
            self.validator.check_all_svg_attribute_values(self.elementname, self.attribs)
        for attribute, value in sorted(self.attribs.items()):
            # filter 'None' values
            if value is not None:
                value = self.value_to_string(value)
                if value:  # just add not empty attributes
                    xml.set(attribute, value)

        for element in self.elements:
            xml.append(element.get_xml())
        xml.append(self.inner_xml)
        return xml


factoryelements['foreignObject'] = ForeignObject


def create_svg_from_trace(trace: Trace):
    total_width = 1280
    total_height = 760
    dwg = svgwrite.Drawing(
        'trace.svg',
        profile='full',
        size=(total_width, total_height),
        style="background-color: " + SolarizedColors.base3.value,
        debug=False,
    )

    dwg.add(
        dwg.script(
            type="application/ecmascript",
            content=renderjson,
        )
    )
    # Add the JavaScript element
    dwg.add(
        dwg.script(
            type="application/ecmascript",
            content="""
                function handleClick(evt) {
                    // implement the zooming functionality and display the rectangle's properties.
                    let target = evt.target;
                    // get the parent of the target
                    let parent = target.parentNode;
                    // get x of parent
                    let left = parent.x.baseVal.value;
                    // get y of parent
                    let top = parent.y.baseVal.value;
                    // set the view_zoom's href to this id
                    let zoom_view = document.getElementById("zoom_view")
                    // if zoom_view is already set to the parent.id, reset to the full_view
                    if (zoom_view.getAttribute("href") == "#" + parent.id) {
                        zoom_view.setAttribute("href", "#full_view");
                        zoom_view.setAttribute("x", 0);
                        zoom_view.setAttribute("y", 0);
                        resetDetails();
                    } else {
                        zoom_view.setAttribute("href", "#" + parent.id);
                        // set the view_zoom's x and y to the negative x and y of the bounding box
                        zoom_view.setAttribute("x", -left);
                        zoom_view.setAttribute("y", -top);
                        updateDetails(parent);
                    }
                }
                """,
        )
    )

    # New code:
    # Create an icicle plot from the trace data.
    # Use the start time of the first node as the start time of the trace.
    start_time = trace.traces[0].start_time_ms
    end_time = trace.traces[-1].end_time_ms

    def traverse_node(node: TraceNode, parent, level: int, parent_start_time_ms: float, parent_duration_ms: float):
        # create a group for node
        node_group = dwg.svg(
            id=str(node.event_id),
            x=(node.start_time_ms - parent_start_time_ms) / parent_duration_ms * 99.5 * svgwrite.percent,
            y="0" if level == 0 else "1.8em",
            width=(node.end_time_ms - node.start_time_ms)
            * 0.99**level
            / parent_duration_ms
            * 99.5
            * svgwrite.percent,
        )
        node_copy = copy.deepcopy(node)
        node_copy.children = []
        node_group["data-raw"] = node_copy.json()
        parent.add(node_group)

        rect = dwg.rect(
            insert=("2px", "0"),
            size=("99.5%", "1.7em"),
            fill=convert_trace_node_kind_to_color(node.kind).value,
            onclick="handleClick(evt)",
            id=f"{str(node.event_id)}_box",
            rx=2,
            ry=2,
        )
        rect["data-id"] = str(node.event_id)
        node_group.add(rect)

        clip_path = dwg.clipPath(id=f"{str(node.event_id)}_clip")
        clip_path.add(
            dwg.rect(
                insert=("4px", "0"),
                size=("99.5%", "1.7em"),
                fill="white",
            )
        )
        dwg.defs.add(clip_path)

        # add a text element for the name of the node
        text = dwg.text(
            node.name,
            insert=(
                "4px",
                "1.35em",
            ),
            fill="black",
            font_size="1em",
            font_family="Arial",
            clip_path=clip_path.get_funciri(),
            pointer_events="none",
        )
        node_group.add(text)

        # traverse children
        for child in node.children:
            traverse_node(child, node_group, level + 1, node.start_time_ms, node.end_time_ms - node.start_time_ms)

    symbol = dwg.symbol(id="full_view")
    dwg.defs.add(symbol)

    for node in trace.traces:
        traverse_node(node, symbol, level=0, parent_start_time_ms=start_time, parent_duration_ms=end_time - start_time)

    zoom_use = dwg.use(id='zoom_view', x=0, y=0, width="100%", height=total_height - 560, href=symbol.get_iri())
    dwg.add(zoom_use)

    details_pane = dwg.foreignObject(
        x=0,
        y=total_height - 560,
        width="100%",
        height=560,
        inner_xml=etree.fromstring(
            """
<html xmlns="http://www.w3.org/1999/xhtml" style="height: 100%;">
<body style="height: 100%; margin: 0px; padding: 2px;">
<div style="height: 100%; display: flex; flex-direction: column; background-color: #eee8d5;">
    <style>
        // Solarized Light Color Scheme (Different Colors for Different Types)
        .renderjson a              { text-decoration: none; }
        .renderjson .syntax        { color: #657b83; }
        .renderjson .string        { color: #2aa198; }
        .renderjson .number        { color: #d33682; }
        .renderjson .boolean       { color: #6c71c4; }
        .renderjson .key           { color: #268bd2; }
        .renderjson .keyword       { color: #859900; }
        .renderjson .object.syntax { color: #b58900; }
        .renderjson .array.syntax  { color: #cb4b16; }
        .renderjson .disclosure    { color: #b58900;
                                     font-size: 150%; }
        .renderjson .syntax.collapsed .disclosure { color: #cb4b16; }
        .renderjson .disclosure:hover    { color: #dc322f; }
        .renderjson .syntax.collapsed .disclosure:hover { color: #d33682; }
        // background for the div
        div {
            color: #657b83;
            font-family: monospace;
            font-size: 14px;
            overflow: auto;
        }
    </style>
    <strong>Click on a node to zoom in and see more details. Click on the zoomed in node to zoom out.</strong>
    <h2>Scope Details</h2>
    <div id="details" style="overflow: auto; font-family: monospace;">
        <table style="border: 1px none black; border-collapse: collapse; width: 100%;">
            <tr style="border: 1px none black; border-collapse: collapse;">
                <th style="border: 1px none black; border-collapse: collapse; text-align: left; width: 30ex;">
                    Property
                </th>
                <th style="border: 1px none black; border-collapse: collapse; text-align: left;"></th>
            </tr>
            <tr style="border: 1px none black; border-collapse: collapse;">
                <td style="border: 1px none black; border-collapse: collapse; text-align: left; width: 30ex;">Name</td>
                <td id="details-name" style="border: 1px none black; border-collapse: collapse; text-align: left;"></td>
            </tr>
            <tr style="border: 1px none black; border-collapse: collapse;">
                <td style="border: 1px none black; border-collapse: collapse; text-align: left; width: 30ex;">
                Kind</td>
                <td id="details-kind" style="border: 1px none black; border-collapse: collapse; text-align: left;"></td>
            </tr>
            <tr style="border: 1px none black; border-collapse: collapse;">
                <td style="border: 1px none black; border-collapse: collapse; text-align: left; width: 30ex;">
                Duration</td>
                <td id="details-duration"
                style="border: 1px none black; border-collapse: collapse; text-align: left;"></td>
            </tr>
            <tr style="border: 1px none black; border-collapse: collapse;">
                <td style="border: 1px none black; border-collapse: collapse; text-align: left; vertical-align: top;
                    width: 30ex;">Exception</td>
                <td id="details-exception"
                style="border: 1px none black; border-collapse: collapse; text-align: left; width: calc(100%-30ex);">
                </td>
            </tr>
            <tr style="border: 1px none black; border-collapse: collapse;">
                <td style="border: 1px none black; border-collapse: collapse; text-align: left; vertical-align: top;
                    width: 30ex;">Result</td>
                <td id="details-result"
                style="border: 1px none black; border-collapse: collapse; text-align: left; width: calc(100%-30ex);">
                </td>
            </tr>
            <tr style="border: 1px none black; border-collapse: collapse;">
                <td style="border: 1px none black; border-collapse: collapse; text-align: left; vertical-align: top;
                    width: 30ex;">Arguments</td>
                <td id="details-arguments"
                style="border: 1px none black; border-collapse: collapse; text-align: left; width: calc(100%-30ex);">
                </td>
            </tr>
            <tr style="border: 1px none black; border-collapse: collapse;">
                <td style="border: 1px none black; border-collapse: collapse; text-align: left; vertical-align: top;
                    width: 30ex;">Self</td>
                <td id="details-self"
                style="border: 1px none black; border-collapse: collapse; text-align: left; width: calc(100%-30ex);">
                </td>
            </tr>
            <tr style="border: 1px none black; border-collapse: collapse;">
                <td style="border: 1px none black; border-collapse: collapse; text-align: left; vertical-align: top;
                    width: 30ex;">Properties</td>
                <td id="details-properties"
                style="border: 1px none black; border-collapse: collapse; text-align: left; width: calc(100%-30ex);">
                </td>
            </tr>
        </table>
    </div>
</div>
</body></html>
            """
        ),
    )
    dwg.add(details_pane)

    dwg.add(
        dwg.script(
            type="application/ecmascript",
            content="""
        function updateDetails(target) {
            let trace_info = JSON.parse(target.dataset.raw);
            let details_name = document.getElementById("details-name");
            let details_kind = document.getElementById("details-kind");
            let details_duration = document.getElementById("details-duration");
            let details_exception = document.getElementById("details-exception");
            let details_result = document.getElementById("details-result");
            let details_arguments = document.getElementById("details-arguments");
            let details_self = document.getElementById("details-self");
            let details_properties = document.getElementById("details-properties");

            var node_name = trace_info.name || "/Unnamed/";
            // add an asterisk if the node is currently running (.running is True)
            if (trace_info.running) {
                node_name += " (*)";
            }
            details_name.innerText = node_name;

            // set kind
            details_kind.innerText = trace_info.kind;

            // set duration
            details_duration.innerText = ((trace_info.end_time_ms - trace_info.start_time_ms) / 1000).toFixed(2) + " s";

            function renderjson_to(node, json) {
                node.innerHTML = "";
                rendered_json = renderjson.set_icons('+', '-').set_show_to_level("all")(json)
                rendered_json.style.whiteSpace = "pre-wrap";
                rendered_json.style.wordWrap = "break-word";
                rendered_json.style.overflow = "auto";
                rendered_json.style.display = "inline-block";
                rendered_json.style.margin = "0";
                node.appendChild(rendered_json);
            }

            // set exception
            let exception = trace_info.properties.exception || "";
            renderjson_to(details_exception, exception);

            // set result
            let result = trace_info.properties.result || "";
            renderjson_to(details_result, result);

            // set arguments
            let arguments = trace_info.properties.arguments || {};
            renderjson_to(details_arguments, arguments);

            // set self
            let self = trace_info.properties.self || {};
            renderjson_to(details_self, self);

            // set properties
            // remove exception, result, arguments, self
            delete trace_info.properties.exception;
            delete trace_info.properties.result;
            delete trace_info.properties.arguments;
            delete trace_info.properties.self;
            let properties = trace_info.properties || {};
            renderjson_to(details_properties, properties);
        }

        function resetDetails() {
            let details_name = document.getElementById("details-name");
            let details_kind = document.getElementById("details-kind");
            let details_duration = document.getElementById("details-duration");
            let details_exception = document.getElementById("details-exception");
            let details_result = document.getElementById("details-result");
            let details_arguments = document.getElementById("details-arguments");
            let details_self = document.getElementById("details-self");
            let details_properties = document.getElementById("details-properties");

            details_name.innerText = "";
            details_kind.innerText = "";
            details_duration.innerText = "";
            details_exception.innerHTML = "";
            details_result.innerHTML = "";
            details_arguments.innerHTML = "";
            details_self.innerHTML = "";
            details_properties.innerHTML = "";
        }
        """,
        )
    )

    return dwg


def save_trace_as_svg(filename: str, trace: Trace):
    tempfile = filename + ".new_tmp"
    svg = create_svg_from_trace(trace)
    svg.saveas(tempfile)
    os.replace(tempfile, filename)


@dataclass
class SvgFileWriter(TraceBuilderEventHandler):
    filename: str

    def on_scope_final(self, builder: 'TraceBuilder'):
        save_trace_as_svg(self.filename, builder.build())


# main
if __name__ == "__main__":
    # load example trace data
    trace = Trace.parse_file("spikes/optimization_unit_trace_ada_2023-05-19_11-07-07.json")
    save_trace_as_svg("trace.svg", trace)
