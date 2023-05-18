import types
import typing
from dataclasses import dataclass

ModuleSpecifier: typing.TypeAlias = types.ModuleType | str
ModuleFilterSpecifier: typing.TypeAlias = typing.Union[ModuleSpecifier, typing.Callable[[str], bool]]
ModuleFilterIterableSpecifier: typing.TypeAlias = typing.Iterable | ModuleFilterSpecifier | None


@dataclass
class OnlyModuleFilter:
    """
    A filter for a module. The filter matches the full module name.
    """

    module_name: str

    def __init__(self, module: ModuleSpecifier):
        if isinstance(module, str):
            self.module_name = module
        elif isinstance(module, types.ModuleType):
            self.module_name = module.__name__
        else:
            raise ValueError(f"Unknown module type {type(module)}")

    def __call__(self, target_module_name: str):
        return target_module_name == self.module_name


@dataclass
class ModulePrefixFilter:
    """
    A filter for a module. The filter matches the module name prefix.
    """

    module_name_prefix: str

    def __init__(self, module_prefix: ModuleSpecifier):
        if isinstance(module_prefix, str):
            self.module_name_prefix = module_prefix
        elif isinstance(module_prefix, types.ModuleType):
            self.module_name_prefix = module_prefix.__name__
        else:
            raise ValueError(f"Unknown module type {type(module_prefix)}")

    def __call__(self, target_module_name: str):
        return target_module_name.startswith(self.module_name_prefix)


def module_filter(module: ModuleSpecifier):
    if isinstance(module, types.ModuleType):
        return OnlyModuleFilter(module.__name__)
    elif isinstance(module, str):
        if module.endswith("*"):
            return ModulePrefixFilter(module[:-1])
        return OnlyModuleFilter(module)
    else:
        raise ValueError(f"Unknown filter type {type(module)} for module {module}")


def convert_module_filter_specifier_to_filter(module_filter_specifier: ModuleFilterSpecifier):
    if isinstance(module_filter_specifier, ModuleSpecifier):  # type: ignore
        return module_filter(module_filter_specifier)  # type: ignore
    elif callable(module_filter_specifier):
        return module_filter_specifier
    else:
        raise ValueError(f"Unknown filter type {type(module_filter_specifier)} for module {module_filter_specifier}")


def convert_module_filter_specifiers_to_filters(module_filter_specifiers: ModuleFilterIterableSpecifier):
    if module_filter_specifiers is None:
        return None
    elif not isinstance(module_filter_specifiers, str) and isinstance(module_filter_specifiers, typing.Iterable):
        assert isinstance(module_filter_specifiers, typing.Iterable)
        return [
            convert_module_filter_specifier_to_filter(module_filter_specifier)
            for module_filter_specifier in module_filter_specifiers  # type: ignore
        ]
    elif isinstance(module_filter_specifiers, ModuleSpecifier):  # type: ignore
        return [module_filter(module_filter_specifiers)]  # type: ignore
    elif callable(module_filter_specifiers):
        return [module_filter_specifiers]
    else:
        raise ValueError(f"Unknown filter type {type(module_filter_specifiers)} for module {module_filter_specifiers}")


def get_top_level_package(module_name: str):
    """
    Returns the top level package name for the given module name.
    """
    return module_name.split(".")[0]


@dataclass
class ModuleFilters:
    """
    Supports filtering of modules using a whitelist (or all) and a blacklist (or none).
    """

    include: list[typing.Callable]
    exclude: list[typing.Callable]

    @classmethod
    def create(cls, include: ModuleFilterIterableSpecifier = None, exclude: ModuleFilterIterableSpecifier = None):
        return cls(
            convert_module_filter_specifiers_to_filters(include), convert_module_filter_specifiers_to_filters(exclude)
        )

    def __call__(self, target_module_name: str):
        if self.include is not None:
            if not any(f(target_module_name) for f in self.include):
                return False
        if self.exclude is not None:
            if any(f(target_module_name) for f in self.exclude):
                return False
        return True


ModuleFiltersSpecifier = ModuleFilterIterableSpecifier | ModuleFilters


def module_filters(module_filters_specifier: ModuleFiltersSpecifier):
    if isinstance(module_filters_specifier, ModuleFilters):
        return module_filters_specifier
    else:
        return ModuleFilters.create(module_filters_specifier)
