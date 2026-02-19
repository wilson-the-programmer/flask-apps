
from flask import Flask, request, render_template_string
import subprocess
import tempfile
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>My Computer</title>
<meta charset="UTF-8">




<!-- CodeMirror CSS -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/theme/ambiance.min.css">

<style>
body {
    background: #1e1e1e;
    color: #e5e5e5;
    font-family: monospace;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
}
.container {
    width: 95%;
    max-width: 940px;
    padding: 25px;
}
.CodeMirror {
    height: 485px;
    font-size: 42px;
    font-weight: bold;
    border: 2px solid white;
}
select, button {
    padding: 14px 18px;
    font-size: 58px;
    margin-top: 12px;
}
.output-box {
    width: 100%;
    height: 500px;
    background: white;
    color: black;
    font-weight: bold;
    text-shadow: 0 0 3px black;
    border: 1px solid #444;
    padding: 14px;
    margin-top: 20px;
    font-size: 40px;
    white-space: pre-wrap;
    overflow-wrap: break-word;
    word-break: break-word;
    overflow-y: scroll;
}


button {
    background-color: black;
    color: white;
    border: 2px solid lightgrey;
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 66px;
    margin-top: 12px;
    cursor: pointer;
    transition: background-color 0.2s, color 0.2s;
}

button:hover {
    background-color: #222;
    color: #aaffaa;
    border-color: lightgrey;
}





</style>

</head>
<body>
<div class="container">

<form method="post" id="code-form">
    <textarea id="code" name="code">{{ code }}</textarea><br>

    <select name="mode" id="mode">
        <option value="python" {% if mode=='python' %}selected{% endif %}>Python</option>
        <option value="sh" {% if mode=='sh' %}selected{% endif %}>Bash</option>
        <option value="c" {% if mode=='c' %}selected{% endif %}>C</option>
        <option value="cpp" {% if mode=='cpp' %}selected{% endif %}>C++</option>
        <option value="html" {% if mode=='html' %}selected{% endif %}>HTML</option>
        <option value="js" {% if mode=='js' %}selected{% endif %}>JavaScript</option>
    </select>

    <button type="button" id="open-btn">Open</button>
    <button type="button" id="save-btn">Save</button>
    <button type="button" id="sys-btn">System </button>
    <button type="button" id="clear-btn">Clear</button>
    <button type="submit" id="run-btn">Run Code</button>
</form>

<input type="file" id="file-input" style="display:none;">

<div class="output-box" id="output">{{ output }}</div>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/python/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/javascript/javascript.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/xml/xml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/css/css.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/htmlmixed/htmlmixed.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/clike/clike.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/shell/shell.min.js"></script>

<script>
const textarea = document.getElementById('code');
const modeSelect = document.getElementById('mode');
const form = document.getElementById('code-form');
const outputBox = document.getElementById('output');
const fileInput = document.getElementById('file-input');
const openBtn = document.getElementById('open-btn');
const saveBtn = document.getElementById('save-btn');
const sysBtn = document.getElementById('sys-btn');
const clearBtn = document.getElementById('clear-btn');

const editor = CodeMirror.fromTextArea(textarea, {
    lineNumbers: true,
    theme: 'ambiance',
    matchBrackets: false,
    autoCloseBrackets: false,
    smartIndent: false,
    electricChars: false,
    indentUnit: 0,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: true
});

editor.setSize("100%", "640px");

function updateMode() {
    const mode = modeSelect.value;
    let cmMode = 'python';
    if(mode === 'python') cmMode = 'python';
    else if(mode === 'c') cmMode = 'text/x-csrc';
    else if(mode === 'cpp') cmMode = 'text/x-c++src';
    else if(mode === 'html') cmMode = 'htmlmixed';
    else if(mode === 'js') cmMode = 'javascript';
    else if(mode === 'sh') cmMode = 'shell';
    editor.setOption('mode', cmMode);
}

modeSelect.addEventListener('change', updateMode);
updateMode();

form.addEventListener('submit', function(e) {
    if(modeSelect.value === 'html') {
        e.preventDefault();
        const htmlWindow = window.open('', '_blank', 'width=1200,height=800');
        htmlWindow.document.write(editor.getValue());
        htmlWindow.document.close();
    } else {
        textarea.value = editor.getValue();
    }
});

openBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
        editor.setValue(ev.target.result);
    };
    reader.readAsText(file);
});

saveBtn.addEventListener('click', () => {
    const blob = new Blob([editor.getValue()], {type: 'text/plain'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'code.txt';
    a.click();
    URL.revokeObjectURL(a.href);
});

clearBtn.addEventListener('click', () => {
    editor.setValue('');
});

sysBtn.addEventListener('click', () => {
    const doc = editor.getDoc();
    const cursor = doc.getCursor();
    const lineNumber = cursor.line;
    const commandLine = doc.getLine(lineNumber).trim();
    if(!commandLine) return;

    fetch(`/sys_command?cmd=${encodeURIComponent(commandLine)}`)
        .then(res => res.text())
        .then(output => {
            doc.replaceRange('\\n' + output + '\\n', {line: lineNumber + 1, ch: 0});
            doc.setCursor({line: lineNumber + 2, ch: 0});
            editor.scrollIntoView({line: lineNumber + 2, ch: 0});
        })
        .catch(err => {
            doc.replaceRange('\\nError: ' + err + '\\n', {line: lineNumber + 1, ch: 0});
            editor.focus()
            editor.scrollIntoView({line: lineNumber + 2, ch: 0});
        });
});
</script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    output = ""
    mode = "python"

    if request.method == "POST":
        code = request.form.get("code", "")
        mode = request.form.get("mode", "")

        if mode == "python":
            try:
                result = subprocess.check_output(["python3", "-c", code], stderr=subprocess.STDOUT).decode()
                output = result
            except subprocess.CalledProcessError as e:
                output = e.output.decode()

        elif mode == "sh":
            try:
                cleaned = code.replace('\r', '')
                result = subprocess.check_output(cleaned, shell=True, stderr=subprocess.STDOUT, executable="/bin/bash").decode()
                output = result
            except subprocess.CalledProcessError as e:
                output = e.output.decode()

        elif mode == "c":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp:
                tmp.write(code.encode())
                tmp.flush()
                exe = tmp.name + ".out"
                comp = subprocess.run(["gcc", tmp.name, "-o", exe], capture_output=True)
                if comp.returncode != 0:
                    output = comp.stderr.decode()
                else:
                    run = subprocess.run([exe], capture_output=True)
                    output = run.stdout.decode() + run.stderr.decode()
                os.unlink(tmp.name)
                if os.path.exists(exe):
                    os.unlink(exe)

        elif mode == "cpp":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as tmp:
                tmp.write(code.encode())
                tmp.flush()
                exe = tmp.name + ".out"
                comp = subprocess.run(["g++", tmp.name, "-o", exe], capture_output=True)
                if comp.returncode != 0:
                    output = comp.stderr.decode()
                else:
                    run = subprocess.run([exe], capture_output=True)
                    output = run.stdout.decode() + run.stderr.decode()
                os.unlink(tmp.name)
                if os.path.exists(exe):
                    os.unlink(exe)

        elif mode == "html":
            output = "HTML code opened in new tab."

        elif mode == "js":
            try:
                run = subprocess.check_output(["node", "-e", code], stderr=subprocess.STDOUT).decode()
                output = run
            except subprocess.CalledProcessError as e:
                output = e.output.decode()

    return render_template_string(HTML, code=code, output=output, mode=mode)

@app.route("/sys_command")
def sys_command():
    cmd = request.args.get("cmd", "")
    if not cmd.strip():
        return ""
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, executable="/bin/bash").decode()
    except subprocess.CalledProcessError as e:
        result = e.output.decode()
    return result

if __name__ == "__main__":
    app.run(port=9000, debug=False)



