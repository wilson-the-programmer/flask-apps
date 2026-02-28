from flask import Flask, request
import subprocess
import sys
import io
import tempfile
import os

app = Flask(__name__)

themes = [
    "3024-day",
    "3024-night",
    "abbott",
    "abcdef",
    "ambiance",
    "ayu-dark",
    "ayu-mirage",
    "base16-dark",
    "base16-light",
    "bespin",
    "blackboard",
    "cobalt",
    "colorforth",
    "darcula",
    "dracula",
    "duotone-dark",
    "duotone-light",
    "eclipse",
    "elegant",
    "erlang-dark",
    "idea",
    "isotope",
    "lesser-dark",
    "liquibyte",
    "lucario",
    "material",
    "material-darker",
    "material-palenight",
    "midnight",
    "mbo",
    "monokai",
    "neo",
    "night",
    "nord",
    "oceanic-next",
    "panda-syntax",
    "paraiso-dark",
    "pastel-on-dark",
    "railscasts",
    "rubyblue",
    "seti",
    "shadowfox",
    "solarized",
    "solarized dark",
    "solarized light",
    "the-matrix",
    "tomorrow-night-bright",
    "ttcn",
    "twilight",
    "vibrant-ink",
    "xq-dark",
    "xq-light",
    "yonce",
    "zenburn",
]
# recommended: tomorrow-night-bright, 

@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    output = ""
    editor_theme = request.args.get("theme", "ambiance")

    if request.method == "POST":
        code = request.form.get("code", "")
        mode = request.form.get("mode", "")
        editor_theme = request.form.get("editor_theme", editor_theme)

        try:
            if mode == "python":
                old_stdout = sys.stdout
                redirected_output = sys.stdout = io.StringIO()
                exec(code, {})
                output = redirected_output.getvalue()
                sys.stdout = old_stdout

            elif mode == "javascript":
                result = subprocess.check_output(
                    ["node", "-e", code], stderr=subprocess.STDOUT
                ).decode()
                output = result

            elif mode == "golang":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".go") as tmp:
                    tmp.write(code.encode())
                    tmp_path = tmp.name
                result = subprocess.check_output(
                    ["go", "run", tmp_path], stderr=subprocess.STDOUT
                ).decode()
                output = result
                os.remove(tmp_path)

            elif mode == "bash":
                result = subprocess.check_output(
                    ["bash", "-c", code], stderr=subprocess.STDOUT
                ).decode()
                output = result

            elif mode == "c":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp:
                    tmp.write(code.encode())
                    tmp_path = tmp.name
                    exe_path = tmp_path + ".out"
                subprocess.check_output(
                    ["gcc", tmp_path, "-o", exe_path], stderr=subprocess.STDOUT
                )
                result = subprocess.check_output(
                    [exe_path], stderr=subprocess.STDOUT
                ).decode()
                output = result
                os.remove(tmp_path)
                os.remove(exe_path)

            elif mode == "rust":
                with tempfile.TemporaryDirectory() as tmpdir:
                    rs_file = os.path.join(tmpdir, "main.rs")
                    exe_file = os.path.join(tmpdir, "main_exe")
                    with open(rs_file, "w") as f:
                        f.write(code)
                    subprocess.check_output(
                        ["rustc", rs_file, "-o", exe_file], stderr=subprocess.STDOUT
                    )
                    result = subprocess.check_output(
                        [exe_file], stderr=subprocess.STDOUT
                    ).decode()
                    output = result

            elif mode.lower() == "html":
                output = code
        except subprocess.CalledProcessError as e:
            output = f"{mode.capitalize()} Error:\n" + e.output.decode()
        except Exception as e:
            output = f"{mode.capitalize()} Error: {e}"

    return f"""
    <html>
    <head>
        <title>Code Runner</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css">
        <link id="cm-theme-css" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/theme/{editor_theme}.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/python/python.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/javascript/javascript.min.js"></script>
        <style>
            body {{
                background-color: #000;
                color: lightgrey;
                font-family: monospace;
                padding: 20px;
            }}
            .CodeMirror {{
                height: 610px;
                width: 100%;
                border: 6px outset #222;
                background: #000;
                color: lightgrey;
                font-size: 15px;
                padding: 8px;
                box-sizing: border-box;
            }}
            .CodeMirror pre {{
                font-size: 15px !important;
                font-weight: bold !important;
                line-height: 1.4 !important;
                font-family: monospace;
                padding: 8px;
            }}
            #output {{
                width: 100%;
                height: 32em;
                font-size: 20px;
                font-weight: bold;
                text-shadow: 0 0 2px black;
                font-family: monospace;
                background-color: white;
                color: black;
                border: 7px solid #555;
                overflow-x: auto;
                white-space: pre-wrap;
                margin-top: 10px;
                padding: 12px;
                box-sizing: border-box;
            }}
            .button-row {{
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }}
            button.code-btn {{
                font-family: monospace, "Courier New";
                font-weight: bold;
                font-size: 36px;
                padding: 15px 0;
                background-color: #333;
                color: beige;
                border: 5px outset white;
                cursor: pointer;
                flex: 1;
                min-width: 0;
                height: 120px;
            }}
        </style>
    </head>
    <body>
        <form method="POST" id="code-form">
            <textarea id="code" name="code" spellcheck="false">{code}</textarea><br>

            <div class="button-row">
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('c')">C ></button>
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('bash')">Bash ></button>
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('javascript')">JS ></button>
                <button class="code-btn" type="button" onclick="full_view()">HTML ></button>
            </div>

            <div class="button-row">
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('golang')">Go ></button>
                <button class="code-btn" type="button" onclick="nextTheme()">Theme</button>
                <button class="code-btn" type="button" onclick="fileInput.click()">Open</button>
                <button class="code-btn" type="button" onclick="saveFile()">Save</button>
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('python')">Python ></button>
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('rust')">Rust ></button>
                <input type="file" id="fileInput" style="display:none" />
                <input type="hidden" name="editor_theme" id="editor_theme_input" value="{editor_theme}">
            </div>

            <textarea id="output" readonly>{output}</textarea>
        </form>

        <script>
            const editor = CodeMirror.fromTextArea(document.getElementById('code'), {{
                mode: "python",
                lineNumbers: false,
                matchBrackets: true,
                autoCloseBrackets: true,
                theme: "{editor_theme}",
                tabSize: 4,
                lineWrapping: true
            }});
            editor.refresh();
            editor.focus();

            const fileInput = document.getElementById('fileInput');
            fileInput.addEventListener('change', function() {{
                const f = this.files[0];
                if (!f) return;
                const reader = new FileReader();
                reader.onload = function(e) {{
                    editor.setValue(e.target.result);
                }};
                reader.readAsText(f);
            }});

            const themes = {themes};
            let themeIndex = themes.indexOf("{editor_theme}");
            if (themeIndex === -1) themeIndex = 0;

            function nextTheme() {{
                themeIndex = (themeIndex + 1) % themes.length;
                const newTheme = themes[themeIndex];
                editor.setOption("theme", newTheme);
                document.getElementById("cm-theme-css").href =
                    `https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/theme/${{newTheme}}.min.css`;
                document.getElementById("editor_theme_input").value = newTheme;
                document.getElementById("output").value += `\\nTheme changed: ${{newTheme}}`;
            }}

            function runCodeFormSubmission(mode) {{
                const form = document.getElementById("code-form");
                const modeInput = document.createElement("input");
                modeInput.type = "hidden";
                modeInput.name = "mode";
                modeInput.value = mode;
                form.appendChild(modeInput);
                form.submit();
            }}

            function full_view() {{
                const code = editor.getValue();
                const blob = new Blob([code], {{ type: 'text/html' }});
                const url = URL.createObjectURL(blob);
                window.open(url, '_blank');
            }}

            function saveFile() {{
                const code = editor.getValue();
                const blob = new Blob([code], {{ type: 'text/plain' }});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = "code.txt";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }}
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(port=8700, debug=False)
