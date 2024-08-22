# MediLearn

## Overview

The MediLearn is an interactive application designed to generate dynamic case studies and provide a simulated mentorship experience. This app leverages the Groq API with the Llama 3 model to create realistic case studies, facilitate interactive chat sessions between a junior doctor and a senior doctor, and evaluate performance based on the interactions.

## Features

- **Case Study Generation**: Generate tailored case studies based on specialization and difficulty level.
- **Interactive Chat**: Simulate a mentorship conversation with a senior doctor to solve the case study.
- **Performance Evaluation**: Assess the junior doctor's diagnostic accuracy, reasoning, and patient management skills based on the chat interaction.
- **User-Friendly Interface**: Easy navigation between case study selection, chat interaction, and performance evaluation.

## Prerequisites

- Python 3.7 or higher
- Streamlit
- Groq Python client library
- `python-dotenv` for environment variable management

## Installation

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment**:

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Setup Environment Variables**:
   Create a folder `.streamlit` and create a file `secrets.toml` in it and add your Groq API key:
   ```dotenv
   [GROQ]
   api_key = "your-groq-api-key"
   ```

## Usage

1. **Run the Application**:

   ```bash
   streamlit run app.py
   ```

2. **Interact with the Application**:
   - **Case Selection**: Choose a specialization and difficulty level, then generate case studies.
   - **Chat Interaction**: Select a case study and engage in a simulated chat with a senior doctor.
   - **Evaluation**: After the chat, evaluate the performance based on the interaction.

## Code Structure

- **app.py**: The main script that handles page setup, case study generation, chat interactions, and performance evaluation.
- **.env**: Contains environment variables such as the Groq API key.
- **requirements.txt**: Lists the Python packages required for the project.

## Dependencies

The `requirements.txt` file includes the following dependencies:

- `streamlit`
- `groq`
- `python-dotenv`
- `toml`
- `plotly`

## Troubleshooting

- **API Key Issues**: Ensure that the API key is correctly set in the `.streamlit/secrets.toml` file.
- **Dependencies**: Verify that all required packages are installed. Use `pip install -r requirements.txt` to install them.
- **Network Issues**: Check your internet connection if there are issues connecting to the Groq API.
