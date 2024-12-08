import os
import logging
import shutil
import sass
import yaml
import json
from jinja2 import Environment, FileSystemLoader

# LOGGER configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

# Paths
SCRIPT_DIR: str = os.path.dirname(__file__)  # This script directory
LOGGER.debug(f'Script directory: {SCRIPT_DIR}')

# Web directories
WEB_DIR: str = os.path.join(SCRIPT_DIR, 'web')
WEB_BLUEPRINTS_DIR: str = os.path.join(WEB_DIR, 'blueprints')
WEB_SRC_DIR: str = os.path.join(WEB_DIR, 'src')
WEB_STATIC_DIR: str = os.path.join(WEB_DIR, 'static')
WEB_TEMPLATES_DIR: str = os.path.join(WEB_DIR, 'templates')

# Dist directory
DIST_DIR: str = os.path.join(os.path.dirname(SCRIPT_DIR), 'dist')
DIST_STATIC_DIR: str = os.path.join(DIST_DIR, 'static')

LOGGER.info(f'Output directory: {DIST_DIR}')
os.makedirs(DIST_DIR, exist_ok=True)
LOGGER.debug(f'Directory {DIST_DIR} created or already existed')


def copy_static_files(static_dir: str, dist_static_dir: str):
    if os.path.isdir(static_dir):
        shutil.copytree(static_dir, dist_static_dir, dirs_exist_ok=True)
        LOGGER.debug(f'Copied static files from {static_dir}')


def render_templates(templates_dir: str, context: dict = {}) -> str:
    index_html: str = os.path.join(templates_dir, 'index.html')
    if os.path.isfile(index_html):

        # Create a Jinja2 environment
        web_templates_dirs: list[str] = [templates_dir, WEB_TEMPLATES_DIR]
        env = Environment(loader=FileSystemLoader(web_templates_dirs))

        # Load the and render the index.html template
        return env.get_template('index.html').render(context)
    else:
        LOGGER.error('index.html template not found')
        return ''


def process_templates(blueprint: str, context: dict = {}):
    templates_dir: str = os.path.join(
        WEB_BLUEPRINTS_DIR, blueprint, 'templates')
    if os.path.isdir(templates_dir):
        output_file: str = os.path.join(DIST_DIR, blueprint, 'index.html')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(render_templates(templates_dir, context))
            LOGGER.debug(f'Written template content to {output_file}')


def compile_scss_files(scss_dir: str, css_dir: str):
    if os.path.isdir(scss_dir):
        sass.compile(dirname=(scss_dir, css_dir), output_style='expanded')


def process_src_files():

    # Compile SCSS files
    scss_dir: str = os.path.join(WEB_SRC_DIR, 'scss')
    css_dir: str = os.path.join(DIST_STATIC_DIR, 'css')
    compile_scss_files(scss_dir, css_dir)


def proccess_data_files(data_dir: str) -> dict:
    data: dict = {}
    if os.path.isdir(data_dir):
        for file_name in os.listdir(data_dir):
            file_path: str = os.path.join(data_dir, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    file, extension = os.path.splitext(file_name)
                    if extension in {'.yaml', '.yml'}:
                        data[file] = yaml.safe_load(f)
                    elif extension == '.json':
                        data[file] = json.load(f)
    return data


def process_blueprint(blueprint: str):

    LOGGER.debug(f'Processing blueprint: {blueprint}')

    # List all files in the home blueprint directory
    blueprint_dir: str = os.path.join(WEB_BLUEPRINTS_DIR, blueprint)
    LOGGER.debug(f'Blueprint files: {os.listdir(blueprint_dir)}')

    # Copy static files
    static_dir: str = os.path.join(blueprint_dir, 'static')
    dist_static_dir: str = os.path.join(DIST_DIR, blueprint, 'static')
    copy_static_files(static_dir, dist_static_dir)

    # Process data files
    data_dir: str = os.path.join(blueprint_dir, 'data')
    context: dict = {'blueprint': blueprint, **proccess_data_files(data_dir)}
    LOGGER.debug(f'Processed data files for {blueprint}: {context}')

    # Process templates
    process_templates(blueprint, context)
    LOGGER.debug(f'Processed templates for {blueprint}')

    # Compile SCSS files
    scss_dir: str = os.path.join(blueprint_dir, 'src', 'scss')
    css_dir: str = os.path.join(DIST_DIR, blueprint, 'static', 'css')
    compile_scss_files(scss_dir, css_dir)
    LOGGER.debug(f'Compiled SCSS files in {scss_dir} to {css_dir}')


def duplicate_index_html():
    index_html: str = os.path.join(DIST_DIR, 'home', 'index.html')
    if os.path.isfile(index_html):
        shutil.copy(index_html, DIST_DIR)
        LOGGER.info(f'Copied home/index.html to {DIST_DIR}')


if __name__ == '__main__':

    # Copy static files
    copy_static_files(WEB_STATIC_DIR, DIST_STATIC_DIR)

    # Process src files
    process_src_files()

    # Get blueprints
    blueprints: list[str] = os.listdir(WEB_BLUEPRINTS_DIR)
    LOGGER.info(f'Blueprints found: {blueprints}')

    for blueprint in blueprints:
        process_blueprint(blueprint)

    duplicate_index_html()
