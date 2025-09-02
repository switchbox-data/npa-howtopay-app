import yaml
from pathlib import Path

def load_all_configs():
    """Load all YAML configuration files and return a dictionary."""
    configs = {}
    data_dir = Path(__file__).parent.parent / "data"
    for yaml_file in data_dir.glob("*.yaml"):
        with open(yaml_file, 'r') as f:
            config_data = yaml.safe_load(f)
            run_name = config_data.get("run_name", yaml_file.stem)
            configs[run_name] = {
                "description": config_data.get("description", f"Configuration from {yaml_file.name}"),
                "config": config_data
            }
    return configs

def load_defaults():
    """Load default values from YAML configuration file."""
    config_path = Path(__file__).parent.parent / "data" / "sample.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_config_value(config, path):
    """Get nested config value"""
    value = config
    for key in path:
        value = value[key]
    return value