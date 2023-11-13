import openai
import streamlit as st
import pandas as pd
import io
import sys
import contextlib

# Set your OpenAI API key
openai.api_key = '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'

def generate_code(data_summary, language, model="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate {language} code for: {data_summary}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return str(e)

def read_data(file, file_type):
    if file_type == 'csv':
        return pd.read_csv(file)
    elif file_type == 'excel':
        return pd.read_excel(file)
    elif file_type == 'json':
        return pd.read_json(file)

def download_button(code, language):
    file_extension = {
        "Python": "py",
        "JavaScript": "js",
        "Java": "java",
        "C++": "cpp",
        "Other": "txt"
    }.get(language, "txt")
    st.download_button(
        label="Download Code",
        data=code,
        file_name=f"generated_code.{file_extension}",
        mime="text/plain"
    )

@contextlib.contextmanager
def capture_output():
    new_out = io.StringIO()
    old_out = sys.stdout
    try:
        sys.stdout = new_out
        yield new_out
    finally:
        sys.stdout = old_out

def execute_generated_code(code, data):
    try:
        local_vars = {'data': data}
        with capture_output() as out:
            exec(code, {}, local_vars)

            # Debugging: Check if 'process_data' function exists and is called
            if 'process_data' in local_vars:
                result = local_vars['process_data'](data)
                if result is not None:
                    print("Result from 'process_data':", result)
                else:
                    print("No result returned from 'process_data'")
            else:
                print("No 'process_data' function found in the generated code.")
        
        # Debugging: Check what was captured
        captured_output = out.getvalue()
        if captured_output:
            print("Captured Output:", captured_output)
        else:
            print("No output was captured.")
        return captured_output
    except Exception as e:
        print("Exception occurred:", e)
        return f"Error in code execution: {e}"

            
# Streamlit UI
#st.title("CodeCraftAI")

logo_url = "https://github.com/raviska/CodeCraft-AI/edit/main/compunnel.png"  # Replace with your logo URL or local path
logo = st.columns([2, 5])  # Adjust the ratio as needed

with logo[0]:
    st.image(logo_url, width=100)  # Adjust width as needed

with logo[1]:
    st.title("CodeCraft AI")



problem_description = st.text_area("Describe the problem or task for the code:")
language = st.selectbox("Select the programming language", ["Python", "JavaScript", "Java", "C++", "Other"])
file_type = st.selectbox("Select file type", ["csv", "excel", "json"])
uploaded_file = st.file_uploader("Upload your data file", type=[file_type])

if uploaded_file is not None:
    data = read_data(uploaded_file, file_type)
    st.write("Data Preview:", data.head())

    data_summary = f"{problem_description}\nData Summary: {data.describe().to_string()}"

    generated_code = None  # Initialize generated_code variable
    if st.button("Generate Code"):
        generated_code = generate_code(data_summary, language)
        st.code(generated_code)
        download_button(generated_code, language)

    # Execute Code button should be inside the same block where generated_code is defined
    if generated_code and st.button("Execute Code"):
        st.write("Executing generated code...")
        execution_result = execute_generated_code(generated_code, data)
        st.write("Execution Result:")
        st.write(execution_result)
