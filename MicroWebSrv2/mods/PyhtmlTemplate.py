
"""
The MIT License (MIT)
Copyright © 2019 Jean-Christophe Bos & HC² (www.hc2.fr)
"""

from   os   import stat
import re

# ============================================================================
# ===( MicroWebSrv2 : PyhtmlTemplate Module )=================================
# ============================================================================

class PyhtmlTemplate :

    _CODE_CONTENT_DEBUG = """\
    <html>
        <head>
            <title>MicroWebSrv2</title>
        </head>
        <body style="font-family: Verdana; background-color: Black; color: White;">
            <h2>MicroWebSrv2 - [500] Internal Server Error</h2>
            <div style="margin: 20px;">
                <h3>PyhtmlTemplate Module Debug</h3>
                <div style="padding: 15px; background-color: Crimson;">
                    Exception in %(path)s<br />
                    %(message)s
                </div>
            </div>
        </body>
    </html>
    """

    # ------------------------------------------------------------------------

    def __init__(self) :
        self._showDebug    = False
        self._pyGlobalVars = { }

    # ------------------------------------------------------------------------

    def OnRequest(self, microWebSrv2, request) :
        if (request.Method == 'GET' or request.Method == 'HEAD') and \
           request.Path.lower().endswith('.pyhtml') :
            filepath = microWebSrv2.ResolvePhysicalPath(request.Path)
            self.ReturnTemplate(microWebSrv2, request, filepath)

    # ------------------------------------------------------------------------

    def ReturnTemplate(self, microWebSrv2, request, filepath):
        if not filepath:
            request.Response.ReturnNotFound()
            return

        try :
            with open(filepath, 'r') as file :
                code = file.read()
        except :
            request.Response.ReturnForbidden()
            return

        try :
            self._pyGlobalVars['Request'] = request
            codeTemplate = CodeTemplate(code, microWebSrv2.HTMLEscape)
            content      = codeTemplate.Execute(self._pyGlobalVars, None)
            request.Response.ReturnOk(content)

        except Exception as ex :
            microWebSrv2.Log( 'Exception raised from pyhtml template file "%s": %s' % (filepath, ex),
                                microWebSrv2.ERROR )
            if self._showDebug :
                request.Response.Return( 500,
                                         PyhtmlTemplate._CODE_CONTENT_DEBUG
                                         % { 'path'    : filepath,
                                             'message' : ex } )
            else :
                request.Response.ReturnInternalServerError()

    # ------------------------------------------------------------------------

    def SetGlobalVar(self, globalVarName, globalVar) :
        if not isinstance(globalVarName, str) or len(globalVarName) == 0 :
            raise ValueError('"globalVarName" must be a not empty string.')
        self._pyGlobalVars[globalVarName] = globalVar

    # ------------------------------------------------------------------------

    def GetGlobalVar(self, globalVarName) :
        if not isinstance(globalVarName, str) or len(globalVarName) == 0 :
            raise ValueError('"globalVarName" must be a not empty string.')
        try :
            return self._pyGlobalVars[globalVarName]
        except :
            return None

    # ------------------------------------------------------------------------

    @property
    def ShowDebug(self) :
        return self._showDebug

    @ShowDebug.setter
    def ShowDebug(self, value) :
        if not isinstance(value, bool) :
            raise ValueError('"ShowDebug" must be a boolean.')
        self._showDebug = value

# ============================================================================
# ===( CodeTemplate )=========================================================
# ============================================================================

class CodeTemplateException(Exception) :
    pass

class CodeTemplate :

    # ------------------------------------------------------------------------

    TOKEN_OPEN              = '{{'
    TOKEN_CLOSE             = '}}'
    TOKEN_OPEN_LEN          = len(TOKEN_OPEN)
    TOKEN_CLOSE_LEN         = len(TOKEN_CLOSE)

    INSTRUCTION_PYTHON      = 'py'
    INSTRUCTION_IF          = 'if'
    INSTRUCTION_ELIF        = 'elif'
    INSTRUCTION_ELSE        = 'else'
    INSTRUCTION_FOR         = 'for'
    INSTRUCTION_END         = 'end'

    RE_IDENTIFIER           = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*$')

    # ------------------------------------------------------------------------

    def __init__(self, code, escapeStrFunc=None) :
        self._code          = code
        self._escapeStrFunc = escapeStrFunc
        self._pos           = 0
        self._endPos        = len(code)-1
        self._line          = 1
        self._pyGlobalVars  = { }
        self._pyLocalVars   = { }
        self._rendered      = ''
        self._instructions  = {
            CodeTemplate.INSTRUCTION_PYTHON : self._processInstructionPYTHON,
            CodeTemplate.INSTRUCTION_IF     : self._processInstructionIF,
            CodeTemplate.INSTRUCTION_ELIF   : self._processInstructionELIF,
            CodeTemplate.INSTRUCTION_ELSE   : self._processInstructionELSE,
            CodeTemplate.INSTRUCTION_FOR    : self._processInstructionFOR,
            CodeTemplate.INSTRUCTION_END    : self._processInstructionEND
        }

    # ------------------------------------------------------------------------

    def Validate(self, pyGlobalVars=None, pyLocalVars=None) :
        try :
            self._parseCode(pyGlobalVars, pyLocalVars, execute=False)
            return None
        except Exception as ex :
            return str(ex)

    # ----------------------------------------------------------------------------

    def Execute(self, pyGlobalVars=None, pyLocalVars=None) :
        try :
            self._parseCode(pyGlobalVars, pyLocalVars, execute=True)
            return self._rendered
        except Exception as ex :
            raise CodeTemplateException(str(ex))

    # ------------------------------------------------------------------------

    def _parseCode(self, pyGlobalVars, pyLocalVars, execute) :
        self._pos          = 0
        self._line         = 1
        self._pyGlobalVars = (pyGlobalVars if isinstance(pyGlobalVars, dict) else { })
        self._pyLocalVars  = (pyLocalVars  if isinstance(pyLocalVars,  dict) else { })
        self._rendered     = ''
        self._pyGlobalVars['print'] = self._renderingPrint
        newTokenToProcess  = self._parseBloc(execute)
        if newTokenToProcess is not None :
            raise CodeTemplateException( '"%s" instruction is not valid here (line %s)'
                                         % (newTokenToProcess, self._line) )

    # ------------------------------------------------------------------------

    def _parseBloc(self, execute) :
        while True :
            idx = self._code.find(CodeTemplate.TOKEN_OPEN, self._pos)
            end = (idx < 0)
            if end :
                idx = self._endPos+1
            code        = self._code[self._pos:idx]
            self._line += code.count('\n')
            if execute :
                self._rendered += code
            if end :
                self._pos = idx
                return None
            self._pos = idx + CodeTemplate.TOKEN_OPEN_LEN
            idx       = self._code.find(CodeTemplate.TOKEN_CLOSE, self._pos)
            if idx < 0 :
                raise CodeTemplateException('"%s" is required but the end of code has been found' % CodeTemplate.TOKEN_CLOSE)
            tokenContent       = self._code[self._pos:idx].strip()
            self._line        += tokenContent.count('\n')
            self._pos          = idx + CodeTemplate.TOKEN_CLOSE_LEN
            newTokenToProcess  = self._processToken(tokenContent, execute)
            if newTokenToProcess is not None :
                return newTokenToProcess

    # ------------------------------------------------------------------------

    def _renderingPrint(self, s) :
        self._rendered += str(s)

    # ------------------------------------------------------------------------

    def _processToken(self, tokenContent, execute) :
        parts        = tokenContent.split(' ', 1)
        instructName = parts[0].strip()
        instructBody = parts[1].strip() if len(parts) > 1 else None
        if len(instructName) == 0 :
            raise CodeTemplateException( '"%s %s" : instruction is missing (line %s)'
                                         % (CodeTemplate.TOKEN_OPEN, CodeTemplate.TOKEN_CLOSE, self._line) )
        newTokenToProcess = None
        if instructName in self._instructions :
            newTokenToProcess = self._instructions[instructName](instructBody, execute)
        elif execute :
            try :
                ret = eval( tokenContent,
                            self._pyGlobalVars,
                            self._pyLocalVars )
                if ret is not None :
                    if (self._escapeStrFunc is not None) :
                        self._rendered += self._escapeStrFunc(str(ret))
                    else :
                        self._rendered += str(ret)
            except Exception as ex :
                raise CodeTemplateException('%s (line %s)' % (ex, self._line))
        return newTokenToProcess

    # ------------------------------------------------------------------------

    def _processInstructionPYTHON(self, instructionBody, execute) :
        if instructionBody is not None :
            raise CodeTemplateException( 'Instruction "%s" is invalid (line %s)'
                                         % (CodeTemplate.INSTRUCTION_PYTHON, self._line) )
        idx = self._code.find(CodeTemplate.TOKEN_OPEN, self._pos)
        if idx < 0 :
            raise CodeTemplateException('"%s" is required but the end of code has been found' % CodeTemplate.TOKEN_OPEN)
        pyCode      = self._code[self._pos:idx]
        self._line += pyCode.count('\n')
        self._pos   = idx + CodeTemplate.TOKEN_OPEN_LEN
        idx         = self._code.find(CodeTemplate.TOKEN_CLOSE, self._pos)
        if idx < 0 :
            raise CodeTemplateException('"%s" is required but the end of code has been found' % CodeTemplate.TOKEN_CLOSE)
        tokenContent  = self._code[self._pos:idx].strip()
        self._line   += tokenContent.count('\n')
        self._pos     = idx + CodeTemplate.TOKEN_CLOSE_LEN
        if tokenContent != CodeTemplate.INSTRUCTION_END :
            raise CodeTemplateException( '"%s" is a bad instruction in a python bloc (line %s)'
                                         % (tokenContent, self._line) )
        if execute :
            lines  = pyCode.split('\n')
            indent = '' 
            for line in lines :
                if len(line.strip()) > 0 :
                    for c in line :
                        if c == ' ' or c == '\t' :
                            indent += c
                        else :
                            break
                    break
            indentLen = len(indent)
            for i in range(len(lines)) :
                if lines[i].startswith(indent) :
                    lines[i] = lines[i][indentLen:] + '\n'
                else :
                    lines[i] += '\n'
            pyCode = ''.join(lines)
            try :
                exec(pyCode, self._pyGlobalVars, self._pyLocalVars)
            except Exception as ex :
                raise CodeTemplateException('%s (line %s)' % (ex, self._line))
        return None

    # ------------------------------------------------------------------------

    def _processInstructionIF(self, instructionBody, execute) :
        if instructionBody is not None :
            if execute :
                try :
                    if (' ' not in instructionBody) and \
                       ('=' not in instructionBody) and \
                       ('<' not in instructionBody) and \
                       ('>' not in instructionBody) and \
                       (instructionBody not in self._pyGlobalVars) and \
                       (instructionBody not in self._pyLocalVars):
                        result = False
                    else:
                        result = bool(eval(instructionBody, self._pyGlobalVars, self._pyLocalVars))
                except Exception as ex :
                    raise CodeTemplateException('%s (line %s)' % (ex, self._line))
            else :
                result = False
            newTokenToProcess = self._parseBloc(execute and result)
            if newTokenToProcess is not None :
                if newTokenToProcess == CodeTemplate.INSTRUCTION_END :
                    return None
                elif newTokenToProcess == CodeTemplate.INSTRUCTION_ELSE :
                    newTokenToProcess = self._parseBloc(execute and not result)
                    if newTokenToProcess is not None :
                        if newTokenToProcess == CodeTemplate.INSTRUCTION_END :
                            return None
                        raise CodeTemplateException( '"%s" instruction waited (line %s)'
                                                     % (CodeTemplate.INSTRUCTION_END, self._line) )
                    raise CodeTemplateException( '"%s" instruction is missing (line %s)'
                                                 % (CodeTemplate.INSTRUCTION_END, self._line) )
                elif newTokenToProcess == CodeTemplate.INSTRUCTION_ELIF :
                    self._processInstructionIF(self._elifInstructionBody, execute and not result)
                    return None
                raise CodeTemplateException( '"%s" instruction waited (line %s)'
                                             % (CodeTemplate.INSTRUCTION_END, self._line) )
            raise CodeTemplateException( '"%s" instruction is missing (line %s)'
                                         % (CodeTemplate.INSTRUCTION_END, self._line) )
        raise CodeTemplateException( '"%s" alone is an incomplete syntax (line %s)'
                                     % (CodeTemplate.INSTRUCTION_IF, self._line) )

    # ------------------------------------------------------------------------

    def _processInstructionELIF(self, instructionBody, execute) :
        if instructionBody is None :
            raise CodeTemplateException( '"%s" alone is an incomplete syntax (line %s)'
                                         % (CodeTemplate.INSTRUCTION_ELIF, self._line) )
        self._elifInstructionBody = instructionBody
        return CodeTemplate.INSTRUCTION_ELIF

    # ------------------------------------------------------------------------

    def _processInstructionELSE(self, instructionBody, execute) :
        if instructionBody is not None :
            raise CodeTemplateException( 'Instruction "%s" is invalid (line %s)'
                                         % (CodeTemplate.INSTRUCTION_ELSE, self._line) )
        return CodeTemplate.INSTRUCTION_ELSE

    # ------------------------------------------------------------------------

    def _processInstructionFOR(self, instructionBody, execute) :
        if instructionBody is not None :
            parts      = instructionBody.split(' ', 1)
            identifier = parts[0].strip()
            if CodeTemplate.RE_IDENTIFIER.match(identifier) is not None and len(parts) > 1 :
                parts = parts[1].strip().split(' ', 1)
                if parts[0] == 'in' and len(parts) > 1 :
                    expression         = parts[1].strip()
                    newTokenToProcess  = None
                    beforePos          = self._pos
                    if execute :
                        try :
                            result = eval(expression, self._pyGlobalVars, self._pyLocalVars)
                        except :
                            raise CodeTemplateException('%s (line %s)' % (str(expression), self._line))
                    if execute and len(result) > 0 :
                        for x in result :
                            self._pyLocalVars[identifier] = x
                            self._pos                     = beforePos
                            newTokenToProcess             = self._parseBloc(True)
                            if newTokenToProcess != CodeTemplate.INSTRUCTION_END :
                                break
                    else :
                        newTokenToProcess = self._parseBloc(False)
                    if newTokenToProcess is not None :
                        if newTokenToProcess == CodeTemplate.INSTRUCTION_END :
                            return None
                        raise CodeTemplateException( '"%s" instruction waited (line %s)'
                                                     % (CodeTemplate.INSTRUCTION_END, self._line) )
                    raise CodeTemplateException( '"%s" instruction is missing (line %s)'
                                                 % (CodeTemplate.INSTRUCTION_END, self._line) )
            raise CodeTemplateException( '"%s %s" is an invalid syntax'
                                         % (CodeTemplate.INSTRUCTION_FOR, instructionBody) )
        raise CodeTemplateException( '"%s" alone is an incomplete syntax (line %s)'
                                     % (CodeTemplate.INSTRUCTION_FOR, self._line) )

    # ------------------------------------------------------------------------

    def _processInstructionEND(self, instructionBody, execute) :
        if instructionBody is not None :
            raise CodeTemplateException( 'Instruction "%s" is invalid (line %s)'
                                         % (CodeTemplate.INSTRUCTION_END, self._line) )
        return CodeTemplate.INSTRUCTION_END

# ============================================================================
# ============================================================================
# ============================================================================
