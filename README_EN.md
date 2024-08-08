# Character Chat LLM

This is a character role-playing chat application based on large language models. It allows users to engage in conversations with predefined characters, supports various language model backends, and provides translation functionality.

## Features

- Multiple character support: Includes several predefined characters such as Mayumi, Reiko, Your_Oblivious_Mother, and more
- Flexible backend: Supports multiple language models, including LocalAI, Baichuan, LLaMA, etc.
- Real-time translation: Uses DeepL API for mixed language translation
- Web interface: Provides a simple chat interface using Flask
- Docker support: Facilitates deployment and scaling

## Dependencies

This project primarily depends on [LocalAI](https://github.com/mudler/LocalAI), a powerful tool for running AI models locally. Before using this project, please ensure that you have correctly installed and configured LocalAI.

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/Alan-333333/charater-chat-llm
   cd character-chat-llm
   ```

2. Build the Docker image:
   ```
   docker build -t charater-chat-llm .
   ```

3. Run the Docker container:
   ```
   docker run -d -p 5000:5000 -e LOCALAI_SERVICE_URL=http://host.docker.internal:8080 charater-chat-llm
   ```

   Note: Ensure that the LocalAI service is running and accessible via the set URL.

### Local Installation

#### Method 1: Using Conda (Recommended)

1. Clone the repository and navigate to the directory:
   ```
   git clone https://github.com/Alan-333333/charater-chat-llm
   cd character-chat-llm
   ```

2. Use the provided setup.sh script to create and configure the Conda environment:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

   This script will automatically create a Conda environment named "charater-chat-llm-env" and install the required dependencies.

3. Activate the environment:
   ```
   conda activate charater-chat-llm-env
   ```

#### Method 2: Using pip

1. Clone the repository and navigate to the directory:
   ```
   git clone https://github.com/Alan-333333/charater-chat-llm
   cd character-chat-llm
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   
   # On Linux or macOS
   ```
   python -m venv venv
   source venv/bin/activate
   ```
   # Or on Windows
 	```
   python -m venv venv
   venv\Scripts\activate
   
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure that the LocalAI service is running.

2. Start the application:
   ```
   python chat_api.py
   ```

3. Visit `http://localhost:5000` in your browser to start chatting.

## Configuration

- Environment variables:
  - `LOCALAI_SERVICE_URL`: URL of the LocalAI service (default is `http://localhost:8080`)

- Character configuration: Add or modify character configuration files in the `characters` directory.

## Project Structure

- `chat_api.py`: Main application entry point
- `backend_localai.py`: LocalAI backend implementation
- `chat.py`: Core chat logic
- `deepl_translate_mixed_lang.py`: DeepL translation functionality
- `templates/`: Web interface templates
- `characters/`: Character images
- `character_configs/`: Character configuration files
- `setup.sh`: Automated environment setup script

## Contributing

Issues and pull requests are welcome.

## License

Please see the `LICENSE` file.