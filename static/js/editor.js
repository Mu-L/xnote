// @author xupingmao
// @since 2018/02/13
// @modified 2019/02/09 18:30:34


// var codeMirror = CodeMirror.fromTextArea(editor, {
//     lineNumbers: true,
//     mode: { name: "text/x-markdown", fencedCodeBlocks: true },
//     lineWrapping: true,
//     fixedGutter: true,
// });

// fixedGutter
// 设置gutter跟随编辑器内容水平滚动（false）还是固定在左侧（true或默认）

/**
 * 初始化codeMirror编辑器
 * @param {string} selector 选择器
 * @param {object} options 可选项
 */
function initCodeMirror(selector, options) {
    var mode = "text/x-sh";
    var name = options.filename || "";
    var height = options.height || "450px";
    var executable = false;

    if (name.endsWith(".py")) {
        mode = "text/x-python";
        // executable = true;
    }
    if (name.endsWith(".js")) {
        mode = "text/javascript";
    } 
    if (name.endsWith(".c")) {
        mode = "text/x-c";
    } 
    if (name.endsWith(".java")) {
        mode = "text/x-java";
    } 
    if (name.endsWith(".md")) {
        mode = "text/x-markdown";
    } 
    if (name.endsWith(".sh") || name.endsWith(".command")) {
        mode = "text/x-sh";
    } 
    if (name.endsWith(".php")) {
        mode = "text/x-php";
    }
    if (name.endsWith(".css")) {
        mode = "text/css";
    }

    if (options.mode) {
        mode = options.mode;
    }

    var keyMap = "default";

    if (CodeMirror.keyMap.sublime) {
        keyMap = "sublime";
    }

    // 补全配置, TODO补上hintWords
    if (CodeMirror.hint) {    
        CodeMirror.defineOption("hintOptions", {
            "hint": CodeMirror.hint.anyword
        });
    }


    var editor = CodeMirror.fromTextArea($(selector)[0], {
        lineNumbers: true,
        mode: mode,
        indentUnit:4,
        lineWrapping: true,
        keyMap: keyMap
        // extraKeys is defined below.
    });
    editor.setSize("auto", height);
    editor.on("update", function (codeMirror, changeObj) {
        $(selector).val(codeMirror.doc.getValue());
    });
    // tab键处理
    editor.setOption("extraKeys", {
        Tab: function(cm) {
            if (cm.somethingSelected()) {
                cm.indentSelection('add');
            } else {            
                var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
                cm.replaceSelection(spaces);
            }
        },
        Ctrl: "autocomplete"
    });

    editor.on("keyup", function (cm, e) {
        // console.log(e);
        var keyCode = e.keyCode;
        
        if ((keyCode >= 97 && keyCode <= 122) 
            || (keyCode >= 65 && keyCode <= 90)
            || keyCode == 95
            || keyCode == 36) {
            // 字母及其他合法变量字符_$
            editor.showHint();
        }
    });

    if (mode == "text/x-python") {
        $("#execute").show();
        $("#execute").click(function (event) {
            var content = editor.doc.getValue();
            $.post("/system/command/python", 
                {content: content} ,
                function (responseText) {
                    var data = responseText;
                    $("#resultDiv").show();
                    $("#result").show().text(data.data);
                });
        })
    }
    return editor;
}


(function () {
    // TODO 处理CJK的宽度, CJK认为是2个字符宽度
    var _padding = '';
    for (var i = 0; i < 1000; i++) {
        _padding += ' ';
    }

    var _isMacOS = navigator.userAgent.indexOf("Mac OS") >= 0;
    function isMacOS() {
        return _isMacOS;
    }
    if (isMacOS()) {
        console.log("Mac OS");
    }

    String.prototype.padLeft = function (size, value) {
        // return _padding.substring(0, size-this.length) + this;
        var text = this;
        while (getStringWidth(text) < size) {
            text += value;
        }
        return text;
    }

    function getCharWidth(c) {
        if (!c) {
            return 0;
        }
        var code = c.charCodeAt(0);
        if (code > 127) {
            if (isMacOS()) {
                // Mac是个奇葩, 3个汉字5个宽度
                return 1.66;
            }
            return 2;
        }
        return 1;
    }

    function getStringWidth(str) {
        if (!str) {
            return 0;
        }
        var width = 0;
        for (var i = 0; i < str.length; i++) {
            width += getCharWidth(str[i]);
        }
        return Math.round(width);
    }

    function formatTable(text) {
        // var text = "name|age|comment\n---|----|--\nCheck No|001|Nothing\nHello中文02|002|中文";
        var lines = text.split('\n');
        var table = [];
        var colWidth = [];

        for (var i = 0; i < lines.length; i++) {
            var row = lines[i];
            var cols = row.split('|');
            table[i] = cols;
            for (var j = 0; j < cols.length; j++) {
                if (cols.length > 1) {                
                    var cell = cols[j].trim();
                    cols[j] = cell;
                    var width = colWidth[j] || 0;
                    colWidth[j] = Math.max(getStringWidth(cell), width);
                }
            }
        }
        console.log(colWidth);

        var newText = "";
        var newLines = [];

        for (var i = 0; i < table.length; i++) {
            var row = table[i];
            if (row.length > 1) {            
                for (var j = 0; j < row.length; j++) {
                    var cell = row[j].trim();
                    if (cell.indexOf('---') >= 0) {
                        row[j] = cell.padLeft(colWidth[j], '-');
                    } else {
                        row[j] = cell.padLeft(colWidth[j], ' ');
                    }
                    
                }
            }
            newLines.push(row.join('|'));
        }
        return newLines.join("\n");
    }

    window.formatMarkdownTable = formatTable;
    
})();


// markdown标题处理
var MarkdownHeading = function() {
    this.text = "";
    this.headings = [];
}

MarkdownHeading.prototype.getParentLevelText = function(info) {
    if (info.parent === null) {
        return "";
    }
    return info.parent.levelText;
}

MarkdownHeading.prototype.getHeadingInfo = function (name, lineNo, prev) {
    var start = 0;
    var level = 0;
    for (var i = 0; i < name.length; i++) {
        if (name[i] === "#") {
            level++;
        }
        if (name[i] === " " || name[i] === "#") {
            start++;
        } else {
            break;
        }
    }

    var levelText = "";
    var lastIndex = 1;
    var parent = null;

    if (prev === null) {
        levelText = "1."
    } else {
        if (level > prev.level) {
            levelText = prev.levelText + "1.";
            lastIndex = 1;
            parent = prev;
        } 

        if (level === prev.level) {
            lastIndex = prev.lastIndex+1;
            levelText = this.getParentLevelText(prev) + lastIndex + ".";
            parent = prev.parent;
        }

        if (level < prev.level) {
            var brother = prev.parent;
            if (brother !== null) {
                lastIndex = brother.lastIndex+1;
                levelText = this.getParentLevelText(brother) + lastIndex + ".";
                parent = brother.parent;
            } else {
                lastIndex = 1;
                levelText = "1.";
            }
        }
    }

    return {
        name: name.substring(start),
        lineNo: lineNo,
        level: level,
        levelText: levelText,
        lastIndex: lastIndex,
        parent: parent
    }
}

MarkdownHeading.prototype.load = function(text) {
    this.text = text;
    this.headings = [];
    var lines = text.split("\n");
    var lineNo = 0;
    var prev = null;
    var isInCode = false;
    var codeTag = "```";

    for (var i = 0; i < lines.length; i++) {
        lineNo++;
        var line = lines[i];
        if (isInCode) {
            // 代码块内部，简单处理下
            if (line.indexOf(codeTag)>=0) {
                isInCode = false;
            }
        } else {
            if (line[0] == "#") {
                var info = this.getHeadingInfo(line, lineNo, prev);
                this.headings.push(info);
                prev = info;
            }
            if (line.indexOf(codeTag)>=0) {
                isInCode = true;
            }
        }
    }
}

MarkdownHeading.prototype.getHeadings = function() {
    return this.headings
}