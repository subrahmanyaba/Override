import logging
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str | Path) -> Dict[str, Any]:
    """
    Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml
        
    Returns:
        Dictionary with validated configuration
        
    Raises:
        FileNotFoundError: If config file is missing
        yaml.YAMLError: If YAML is malformed
        KeyError: If required keys are missing
    """
    logger = logging.getLogger(__name__)
    config_file = Path(config_path)
    
    # Check if file exists
    if not config_file.exists():
        error_msg = f"Config file not found: {config_file.absolute()}"
        logger.critical(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            
        # Validate required keys
        required_keys = ['media_library', 'mixing']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required config key: {key}")
                
        logger.info(f"Loaded config from {config_file}")
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {config_file}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise