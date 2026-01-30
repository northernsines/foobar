const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

/**
 * FOOBAR Language Support Extension v2.0
 * Comprehensive IntelliSense for all standard library features + user-defined symbols
 */

// Built-in FOOBAR types and keywords
const FOOBAR_TYPES = [
    'boolean', 'integer', 'longinteger', 'float', 'longfloat', 
    'string', 'character', 'void'
];

const FOOBAR_KEYWORDS = [
    'class', 'inherits', 'public', 'private', 'new', 'thisclass', 
    'parent', 'isa', 'if', 'elseif', 'else', 'loop', 'for', 'until',
    'while', 'return', 'break', 'continue', 'true', 'false', 'Main', 
    'Initialize', 'enumerated', 'foreach'
];

const FOOBAR_OPERATORS = [
    '++', '--', '+', '-', '*', '/', '%', '^', '==', '>=', '<=', '>', '<',
    '&', 'V', 'VV', 'not()', 'and', 'or', 'not'
];

// CONSOLE class methods
const CONSOLE_METHODS = {
    'Print': {
        signature: 'CONSOLE.Print(string message)',
        documentation: 'Prints a string message to the console',
        detail: 'void Print(string)',
        parameters: ['message']
    },
    'PrintInteger': {
        signature: 'CONSOLE.PrintInteger(integer value)',
        documentation: 'Prints an integer to the console',
        detail: 'void PrintInteger(integer)',
        parameters: ['value']
    },
    'PrintFloat': {
        signature: 'CONSOLE.PrintFloat(float value)',
        documentation: 'Prints a float to the console',
        detail: 'void PrintFloat(float)',
        parameters: ['value']
    },
    'PrintBoolean': {
        signature: 'CONSOLE.PrintBoolean(boolean value)',
        documentation: 'Prints a boolean to the console',
        detail: 'void PrintBoolean(boolean)',
        parameters: ['value']
    },
    'Scan': {
        signature: 'CONSOLE.Scan()',
        documentation: 'Reads a line of text from input',
        detail: 'string Scan()',
        parameters: []
    },
    'ScanInteger': {
        signature: 'CONSOLE.ScanInteger()',
        documentation: 'Reads an integer from input',
        detail: 'integer ScanInteger()',
        parameters: []
    },
    'ScanFloat': {
        signature: 'CONSOLE.ScanFloat()',
        documentation: 'Reads a float from input',
        detail: 'float ScanFloat()',
        parameters: []
    },
    'ScanBoolean': {
        signature: 'CONSOLE.ScanBoolean()',
        documentation: 'Reads a boolean from input',
        detail: 'boolean ScanBoolean()',
        parameters: []
    },
    'Clear': {
        signature: 'CONSOLE.Clear()',
        documentation: 'Clears the terminal screen',
        detail: 'void Clear()',
        parameters: []
    }
};

// MATH class methods
const MATH_METHODS = {
    'min': {
        signature: 'MATH.Min(integer a, integer b)',
        documentation: 'Returns the minimum of two integers',
        detail: 'integer min(integer, integer)',
        parameters: ['a', 'b']
    },
    'max': {
        signature: 'MATH.Max(integer a, integer b)',
        documentation: 'Returns the maximum of two integers',
        detail: 'integer max(integer, integer)',
        parameters: ['a', 'b']
    },
    'absolute': {
        signature: 'MATH.Absolute(integer value)',
        documentation: 'Returns the absolute value',
        detail: 'integer absolute(integer)',
        parameters: ['value']
    },
    'squareRoot': {
        signature: 'MATH.SquareRoot(float value)',
        documentation: 'Returns the square root',
        detail: 'float squareRoot(float)',
        parameters: ['value']
    },
    'power': {
        signature: 'MATH.Power(float base, float exponent)',
        documentation: 'Returns base raised to exponent',
        detail: 'float power(float, float)',
        parameters: ['base', 'exponent']
    },
    'floor': {
        signature: 'MATH.Floor(float value)',
        documentation: 'Rounds down to nearest integer',
        detail: 'integer floor(float)',
        parameters: ['value']
    },
    'ceil': {
        signature: 'MATH.Ceil(float value)',
        documentation: 'Rounds up to nearest integer',
        detail: 'integer ceil(float)',
        parameters: ['value']
    },
    'round': {
        signature: 'MATH.Round(float value)',
        documentation: 'Rounds to nearest integer',
        detail: 'integer round(float)',
        parameters: ['value']
    },
    'sine': {
        signature: 'MATH.Sine(float radians)',
        documentation: 'Returns sine of angle in radians',
        detail: 'float sine(float)',
        parameters: ['radians']
    },
    'cosine': {
        signature: 'MATH.Cosine(float radians)',
        documentation: 'Returns cosine of angle in radians',
        detail: 'float cosine(float)',
        parameters: ['radians']
    },
    'tangent': {
        signature: 'MATH.Tangent(float radians)',
        documentation: 'Returns tangent of angle in radians',
        detail: 'float tangent(float)',
        parameters: ['radians']
    },
    'random': {
        signature: 'MATH.Random()',
        documentation: 'Returns random float between 0.0 and 1.0',
        detail: 'float random()',
        parameters: []
    },
    'clamp': {
        signature: 'MATH.Clamp(integer value, integer min, integer max)',
        documentation: 'Clamps value between min and max',
        detail: 'integer clamp(integer, integer, integer)',
        parameters: ['value', 'min', 'max']
    },
    'PI': {
        signature: 'MATH.PI',
        documentation: 'Mathematical constant π (3.14159...)',
        detail: 'const float PI',
        parameters: [],
        isConstant: true
    },
    'E': {
        signature: 'MATH.E',
        documentation: 'Mathematical constant e (2.71828...)',
        detail: 'const float E',
        parameters: [],
        isConstant: true
    }
};

// STRING class methods
const STRING_METHODS = {
    'Contains': {
        signature: 'STRING.Contains(string text, string search)',
        documentation: 'Checks if text contains search string',
        detail: 'boolean Contains(string, string)',
        parameters: ['text', 'search']
    },
    'StartsWith': {
        signature: 'STRING.StartsWith(string text, string prefix)',
        documentation: 'Checks if text starts with prefix',
        detail: 'boolean StartsWith(string, string)',
        parameters: ['text', 'prefix']
    },
    'EndsWith': {
        signature: 'STRING.EndsWith(string text, string suffix)',
        documentation: 'Checks if text ends with suffix',
        detail: 'boolean EndsWith(string, string)',
        parameters: ['text', 'suffix']
    },
    'Join': {
        signature: 'STRING.Join(array items, string delimiter)',
        documentation: 'Joins array elements with delimiter',
        detail: 'string Join(array, string)',
        parameters: ['items', 'delimiter']
    }
};

// String instance methods
const STRING_INSTANCE_METHODS = {
    'length': {
        signature: 'string.length()',
        documentation: 'Returns the length of the string',
        detail: 'integer length()',
        parameters: []
    },
    'substring': {
        signature: 'string.substring(integer start, integer end)',
        documentation: 'Returns substring from start to end index',
        detail: 'string substring(integer, integer)',
        parameters: ['start', 'end']
    },
    'toUpper': {
        signature: 'string.toUpper()',
        documentation: 'Converts string to uppercase',
        detail: 'string toUpper()',
        parameters: []
    },
    'toLower': {
        signature: 'string.toLower()',
        documentation: 'Converts string to lowercase',
        detail: 'string toLower()',
        parameters: []
    },
    'replace': {
        signature: 'string.replace(string old, string new)',
        documentation: 'Replaces all occurrences of old with new',
        detail: 'string replace(string, string)',
        parameters: ['old', 'new']
    },
    'trim': {
        signature: 'string.trim()',
        documentation: 'Removes leading and trailing whitespace',
        detail: 'string trim()',
        parameters: []
    },
    'toInteger': {
        signature: 'string.toInteger()',
        documentation: 'Parses string as integer',
        detail: 'integer toInteger()',
        parameters: []
    },
    'toFloat': {
        signature: 'string.toFloat()',
        documentation: 'Parses string as float',
        detail: 'float toFloat()',
        parameters: []
    }
};

// Integer instance methods
const INTEGER_INSTANCE_METHODS = {
    'toString': {
        signature: 'integer.toString()',
        documentation: 'Converts integer to string',
        detail: 'string toString()',
        parameters: []
    }
};

// Float instance methods
const FLOAT_INSTANCE_METHODS = {
    'toString': {
        signature: 'float.toString()',
        documentation: 'Converts float to string',
        detail: 'string toString()',
        parameters: []
    }
};

// DATETIME class methods
const DATETIME_METHODS = {
    'Now': {
        signature: 'DATETIME.Now()',
        documentation: 'Returns current Unix timestamp',
        detail: 'integer Now()',
        parameters: []
    },
    'Year': {
        signature: 'DATETIME.Year(integer timestamp)',
        documentation: 'Extracts year from timestamp',
        detail: 'integer Year(integer)',
        parameters: ['timestamp']
    },
    'Month': {
        signature: 'DATETIME.Month(integer timestamp)',
        documentation: 'Extracts month (1-12) from timestamp',
        detail: 'integer Month(integer)',
        parameters: ['timestamp']
    },
    'Day': {
        signature: 'DATETIME.Day(integer timestamp)',
        documentation: 'Extracts day of month from timestamp',
        detail: 'integer Day(integer)',
        parameters: ['timestamp']
    },
    'Hour': {
        signature: 'DATETIME.Hour(integer timestamp)',
        documentation: 'Extracts hour (0-23) from timestamp',
        detail: 'integer Hour(integer)',
        parameters: ['timestamp']
    },
    'Minute': {
        signature: 'DATETIME.Minute(integer timestamp)',
        documentation: 'Extracts minute (0-59) from timestamp',
        detail: 'integer Minute(integer)',
        parameters: ['timestamp']
    },
    'Second': {
        signature: 'DATETIME.Second(integer timestamp)',
        documentation: 'Extracts second (0-59) from timestamp',
        detail: 'integer Second(integer)',
        parameters: ['timestamp']
    }
};

// RANDOM class methods
const RANDOM_METHODS = {
    'Integer': {
        signature: 'RANDOM.Integer(integer min, integer max)',
        documentation: 'Returns random integer between min and max (inclusive)',
        detail: 'integer Integer(integer, integer)',
        parameters: ['min', 'max']
    },
    'Float': {
        signature: 'RANDOM.Float(float min, float max)',
        documentation: 'Returns random float between min and max',
        detail: 'float Float(float, float)',
        parameters: ['min', 'max']
    },
    'Character': {
        signature: 'RANDOM.Character()',
        documentation: 'Returns random printable ASCII character',
        detail: 'character Character()',
        parameters: []
    },
    'Boolean': {
        signature: 'RANDOM.Boolean()',
        documentation: 'Returns random boolean (true or false)',
        detail: 'boolean Boolean()',
        parameters: []
    },
    'Seed': {
        signature: 'RANDOM.Seed(integer value)',
        documentation: 'Sets the random number generator seed',
        detail: 'void Seed(integer)',
        parameters: ['value']
    }
};

// FILE class methods
const FILE_METHODS = {
    'Read': {
        signature: 'FILE.Read(string path)',
        documentation: 'Reads contents of file at path',
        detail: 'string Read(string)',
        parameters: ['path']
    },
    'Write': {
        signature: 'FILE.Write(string path, string content)',
        documentation: 'Writes content to file at path',
        detail: 'boolean Write(string, string)',
        parameters: ['path', 'content']
    },
    'Append': {
        signature: 'FILE.Append(string path, string content)',
        documentation: 'Appends content to file at path',
        detail: 'boolean Append(string, string)',
        parameters: ['path', 'content']
    },
    'Exists': {
        signature: 'FILE.Exists(string path)',
        documentation: 'Checks if file exists at path',
        detail: 'boolean Exists(string)',
        parameters: ['path']
    },
    'Delete': {
        signature: 'FILE.Delete(string path)',
        documentation: 'Deletes file at path',
        detail: 'boolean Delete(string)',
        parameters: ['path']
    }
};

// Array methods
const ARRAY_METHODS = {
    'length': {
        signature: 'array.length',
        documentation: 'Returns the number of elements in the array',
        detail: 'integer length',
        parameters: [],
        isProperty: true  // Mark as property so no () are added
    },
    'map': {
        signature: 'array.map(lambda)',
        documentation: 'Transforms each element using a lambda function',
        detail: 'array map(lambda)',
        parameters: ['transform'],
        example: 'numbers.map(x -> x * 2)'
    },
    'filter': {
        signature: 'array.filter(lambda)',
        documentation: 'Filters elements based on condition',
        detail: 'array filter(lambda)',
        parameters: ['condition'],
        example: 'numbers.filter(x -> x > 5)'
    },
    'reduce': {
        signature: 'array.reduce(lambda, initial)',
        documentation: 'Reduces array to single value',
        detail: 'value reduce(lambda, value)',
        parameters: ['accumulator', 'initial'],
        example: 'numbers.reduce((acc, x) -> acc + x, 0)'
    },
    'sort': {
        signature: 'array.sort()',
        documentation: 'Sorts array in ascending order',
        detail: 'array sort()',
        parameters: [],
        example: 'numbers.sort()'
    },
    'unique': {
        signature: 'array.unique()',
        documentation: 'Removes duplicate elements',
        detail: 'array unique()',
        parameters: [],
        example: 'numbers.unique()'
    },
    'find': {
        signature: 'array.find(lambda)',
        documentation: 'Finds first element matching condition',
        detail: 'element find(lambda)',
        parameters: ['condition'],
        example: 'numbers.find(x -> x > 10)'
    },
    'print': {
        signature: 'array.print()',
        documentation: 'Prints array to console',
        detail: 'void print()',
        parameters: [],
        example: 'numbers.print()'
    }
};

// All static classes for completion
const STATIC_CLASSES = {
    'CONSOLE': CONSOLE_METHODS,
    'MATH': MATH_METHODS,
    'STRING': STRING_METHODS,
    'DATETIME': DATETIME_METHODS,
    'RANDOM': RANDOM_METHODS,
    'FILE': FILE_METHODS
};

/**
 * Parse a .foob file and extract symbols (classes, methods, variables)
 */
function parseFileSymbols(fileContent) {
    const symbols = {
        classes: {}, // className -> {methods: [], fields: []}
        variables: [], // variable names in current file
        imports: [] // imported file paths
    };

    // Extract imports
    const importRegex = /import\s+"([^"]+)";/g;
    let match;
    while ((match = importRegex.exec(fileContent)) !== null) {
        symbols.imports.push(match[1]);
    }

    // Extract class definitions
    const classRegex = /class\s+([A-Z_][A-Z0-9_]*)\s*(?:inherits\s+[^{]+)?\s*{/g;
    while ((match = classRegex.exec(fileContent)) !== null) {
        const className = match[1];
        symbols.classes[className] = { methods: [], fields: [] };

        // Find the class body (everything until matching })
        const classStart = match.index + match[0].length;
        let braceCount = 1;
        let classEnd = classStart;
        
        for (let i = classStart; i < fileContent.length && braceCount > 0; i++) {
            if (fileContent[i] === '{') braceCount++;
            if (fileContent[i] === '}') braceCount--;
            classEnd = i;
        }

        const classBody = fileContent.substring(classStart, classEnd);

        // Extract methods from class body
        const methodRegex = /(?:public|private)?\s+(?:static\s+)?(?:void|boolean|integer|longinteger|float|longfloat|string|character|[A-Z_][A-Z0-9_]*(?:\[\])?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
        let methodMatch;
        while ((methodMatch = methodRegex.exec(classBody)) !== null) {
            const methodName = methodMatch[1];
            
            // Extract parameters
            const paramStart = methodMatch.index + methodMatch[0].length;
            let paramEnd = paramStart;
            let parenCount = 1;
            
            for (let i = paramStart; i < classBody.length && parenCount > 0; i++) {
                if (classBody[i] === '(') parenCount++;
                if (classBody[i] === ')') parenCount--;
                paramEnd = i;
            }
            
            const paramsString = classBody.substring(paramStart, paramEnd);
            const params = paramsString
                .split(',')
                .map(p => p.trim())
                .filter(p => p.length > 0)
                .map(p => {
                    const parts = p.trim().split(/\s+/);
                    return parts[parts.length - 1]; // Get parameter name
                });

            symbols.classes[className].methods.push({
                name: methodName,
                parameters: params
            });
        }

        // Extract fields from class body
        const fieldRegex = /(?:public|private)?\s+(?:static\s+)?(?:boolean|integer|longinteger|float|longfloat|string|character|[A-Z_][A-Z0-9_]*(?:\[\])?)\s+([a-z_][A-Za-z0-9_]*)\s*;/g;
        let fieldMatch;
        while ((fieldMatch = fieldRegex.exec(classBody)) !== null) {
            symbols.classes[className].fields.push(fieldMatch[1]);
        }
    }

    // Extract local variables (simplified - just variable declarations)
    const varRegex = /(?:boolean|integer|longinteger|float|longfloat|string|character|[A-Z_][A-Z0-9_]*(?:\[\])?)\s+([a-z_][A-Za-z0-9_]*)\s*(?:=|;)/g;
    while ((match = varRegex.exec(fileContent)) !== null) {
        const varName = match[1];
        if (!symbols.variables.includes(varName)) {
            symbols.variables.push(varName);
        }
    }

    return symbols;
}

/**
 * Resolve import path relative to current file
 */
function resolveImportPath(currentFilePath, importPath) {
    const currentDir = path.dirname(currentFilePath);
    let resolved = path.join(currentDir, importPath);
    
    // Add .foob extension if not present
    if (!resolved.endsWith('.foob')) {
        resolved += '.foob';
    }
    
    return resolved;
}

/**
 * Get symbols from imported files
 */
function getImportedSymbols(currentFilePath, fileContent) {
    const allSymbols = {
        classes: {},
        variables: []
    };

    const currentSymbols = parseFileSymbols(fileContent);
    
    // Add current file's symbols
    Object.assign(allSymbols.classes, currentSymbols.classes);
    allSymbols.variables = [...currentSymbols.variables];

    // Process imports
    for (const importPath of currentSymbols.imports) {
        try {
            const resolvedPath = resolveImportPath(currentFilePath, importPath);
            
            if (fs.existsSync(resolvedPath)) {
                const importedContent = fs.readFileSync(resolvedPath, 'utf8');
                const importedSymbols = parseFileSymbols(importedContent);
                
                // Merge imported symbols
                Object.assign(allSymbols.classes, importedSymbols.classes);
            }
        } catch (err) {
            // Silently ignore import errors in autocomplete
            console.log(`Could not load import: ${importPath}`, err);
        }
    }

    return allSymbols;
}

/**
 * Get the type of a variable by looking backwards in the document
 */
function getVariableType(document, position, varName) {
    // Search backwards for variable declaration
    for (let line = position.line; line >= 0; line--) {
        const lineText = document.lineAt(line).text;
        
        // Look for variable declaration: TYPE varName
        const declRegex = new RegExp(`([A-Z_][A-Z0-9_]*)\\s+${varName}\\s*[=;]`);
        const match = lineText.match(declRegex);
        
        if (match) {
            return match[1]; // Return the type (class name)
        }
    }
    
    return null;
}

/**
 * Create completion item from method info
 */
function createCompletionItem(name, info, kind = vscode.CompletionItemKind.Method) {
    const item = new vscode.CompletionItem(name, kind);
    item.detail = info.detail;
    
    let docs = info.documentation;
    if (info.example) {
        docs += `\n\n**Example:**\n\`\`\`foobar\n${info.example}\n\`\`\``;
    }
    item.documentation = new vscode.MarkdownString(docs);
    
    // Handle properties (no parentheses)
    if (info.isProperty) {
        item.insertText = name;
        item.kind = vscode.CompletionItemKind.Property;
    }
    // Handle constants (no parentheses)
    else if (info.isConstant) {
        item.insertText = name;
        item.kind = vscode.CompletionItemKind.Constant;
    }
    // Handle methods with parameters (add snippet)
    else if (info.parameters && info.parameters.length > 0) {
        const params = info.parameters.map((p, i) => `\${${i+1}:${p}}`).join(', ');
        item.insertText = new vscode.SnippetString(`${name}(${params})`);
    }
    // Handle methods without parameters (add empty parentheses)
    else {
        item.insertText = new vscode.SnippetString(`${name}()`);
    }
    
    return item;
}

/**
 * Activation function
 */
function activate(context) {
    console.log('FOOBAR Language Support v2.1 is now active with user symbols!');

    // Register completion provider
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        'foobar',
        {
            provideCompletionItems(document, position) {
                const linePrefix = document.lineAt(position).text.substr(0, position.character);
                const completions = [];

                console.log('Completion triggered! Line prefix:', linePrefix);

                // Get symbols from current file and imports
                const filePath = document.fileName;
                const fileContent = document.getText();
                const userSymbols = getImportedSymbols(filePath, fileContent);

                console.log('User symbols:', Object.keys(userSymbols.classes), userSymbols.variables);

                // Check for static class method completion (e.g., CONSOLE., MATH., etc.)
                for (const [className, methods] of Object.entries(STATIC_CLASSES)) {
                    if (linePrefix.endsWith(`${className}.`)) {
                        for (const [methodName, info] of Object.entries(methods)) {
                            completions.push(createCompletionItem(methodName, info));
                        }
                        return completions;
                    }
                }

                // Check for user-defined class method completion
                for (const [className, classInfo] of Object.entries(userSymbols.classes)) {
                    if (linePrefix.endsWith(`${className}.`)) {
                        // Add methods from this class
                        for (const method of classInfo.methods) {
                            const item = new vscode.CompletionItem(method.name, vscode.CompletionItemKind.Method);
                            item.detail = `${className}.${method.name}()`;
                            
                            if (method.parameters && method.parameters.length > 0) {
                                const params = method.parameters.map((p, i) => `\${${i+1}:${p}}`).join(', ');
                                item.insertText = new vscode.SnippetString(`${method.name}(${params})`);
                            } else {
                                item.insertText = new vscode.SnippetString(`${method.name}()`);
                            }
                            
                            completions.push(item);
                        }
                        return completions;
                    }
                }

                // Check for instance method completion (e.g., variable.)
                const instanceMatch = linePrefix.match(/([a-z_][A-Za-z0-9_]*)\.\w*$/);
                if (instanceMatch) {
                    const varName = instanceMatch[1];
                    
                    // Try to determine the type of this variable
                    const varType = getVariableType(document, position, varName);
                    
                    if (varType && userSymbols.classes[varType]) {
                        // Add methods from the variable's class
                        const classInfo = userSymbols.classes[varType];
                        for (const method of classInfo.methods) {
                            const item = new vscode.CompletionItem(method.name, vscode.CompletionItemKind.Method);
                            item.detail = `${varType}.${method.name}()`;
                            
                            if (method.parameters && method.parameters.length > 0) {
                                const params = method.parameters.map((p, i) => `\${${i+1}:${p}}`).join(', ');
                                item.insertText = new vscode.SnippetString(`${method.name}(${params})`);
                            } else {
                                item.insertText = new vscode.SnippetString(`${method.name}()`);
                            }
                            
                            completions.push(item);
                        }
                        return completions;
                    }
                }

                // Check for any dot completion (could be string, array, number, etc.)
                if (linePrefix.match(/\.\w*$/)) {
                    // Add all instance methods
                    for (const [methodName, info] of Object.entries(STRING_INSTANCE_METHODS)) {
                        completions.push(createCompletionItem(methodName, info));
                    }
                    for (const [methodName, info] of Object.entries(ARRAY_METHODS)) {
                        completions.push(createCompletionItem(methodName, info));
                    }
                    for (const [methodName, info] of Object.entries(INTEGER_INSTANCE_METHODS)) {
                        completions.push(createCompletionItem(methodName, info));
                    }
                    for (const [methodName, info] of Object.entries(FLOAT_INSTANCE_METHODS)) {
                        completions.push(createCompletionItem(methodName, info));
                    }
                    return completions;
                }

                // Add types
                for (const type of FOOBAR_TYPES) {
                    const item = new vscode.CompletionItem(type, vscode.CompletionItemKind.TypeParameter);
                    completions.push(item);
                }

                // Add keywords
                for (const keyword of FOOBAR_KEYWORDS) {
                    const item = new vscode.CompletionItem(keyword, vscode.CompletionItemKind.Keyword);
                    completions.push(item);
                }

                // Add static classes (built-in)
                for (const className of Object.keys(STATIC_CLASSES)) {
                    const item = new vscode.CompletionItem(className, vscode.CompletionItemKind.Class);
                    item.detail = `${className} class`;
                    completions.push(item);
                }

                // Add user-defined classes
                for (const className of Object.keys(userSymbols.classes)) {
                    const item = new vscode.CompletionItem(className, vscode.CompletionItemKind.Class);
                    item.detail = `class ${className}`;
                    completions.push(item);
                }

                // Add user variables
                for (const varName of userSymbols.variables) {
                    const item = new vscode.CompletionItem(varName, vscode.CompletionItemKind.Variable);
                    completions.push(item);
                }

                return completions;
            }
        },
        '.' // Trigger on dot
    );

    // Register hover provider
    const hoverProvider = vscode.languages.registerHoverProvider('foobar', {
        provideHover(document, position) {
            const wordRange = document.getWordRangeAtPosition(position);
            if (!wordRange) return;

            const word = document.getText(wordRange);

            // Check all static class methods
            for (const [className, methods] of Object.entries(STATIC_CLASSES)) {
                if (methods[word]) {
                    const info = methods[word];
                    const content = new vscode.MarkdownString();
                    content.appendCodeblock(info.signature, 'foobar');
                    content.appendText(info.documentation);
                    return new vscode.Hover(content);
                }
            }

            // Check string instance methods
            if (STRING_INSTANCE_METHODS[word]) {
                const info = STRING_INSTANCE_METHODS[word];
                const content = new vscode.MarkdownString();
                content.appendCodeblock(info.signature, 'foobar');
                content.appendText(info.documentation);
                return new vscode.Hover(content);
            }

            // Check array methods
            if (ARRAY_METHODS[word]) {
                const info = ARRAY_METHODS[word];
                const content = new vscode.MarkdownString();
                content.appendCodeblock(info.signature, 'foobar');
                content.appendText(info.documentation);
                if (info.example) {
                    content.appendMarkdown(`\n\n**Example:**\n\`\`\`foobar\n${info.example}\n\`\`\``);
                }
                return new vscode.Hover(content);
            }

            return undefined;
        }
    });

    context.subscriptions.push(completionProvider, hoverProvider);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
