import pynecone as pc

config = pc.Config(
    app_name="app",
    db_url="sqlite:///pynecone.db",
    port=3333,
    backend_port=8333,
    api_url="http://localhost:8333",
    env=pc.Env.DEV,
    frontend_packages=[
        "react-flame-graph",
        "react-object-view",
        "react-json-view-lite",
    ],
)
