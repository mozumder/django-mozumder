from mozumder.template import Block

class head(Block):

    inline_head_css="""
            body {margin: 2% auto 5% auto; background: #fdfdf2; color: #111; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 16px; line-height: 1.8; text-shadow: 0 1px 0 #ffffff; max-width: 73%;}
            h1, h2, h3, h4 {line-height:1.2}
            h2, h3 {color: #777}
            code {background: white;}
            a {border-bottom: 1px solid #444444; color: #444444; text-decoration: none;}
            a:hover {border-bottom: 0;}
            .fixed {
    white-space: nowrap;
    vertical-align:top;
}
table {
  table-layout: fixed;
}
            """

    vary = ['id', 'session_key']

    def generate_html(self,request,context=None):
        return f'<title>{page.data.title}</title></head><body><h4><a href="/">Hello World</a></h4>'


from .template import MozumderTemplate


class add(MozumderTemplate):

    blocks = [head]


from dataclasses import dataclass

@dataclass
class MozumderHTMLMessageTemplate:
    message: str

from mozumder.template.components import raw

class MessagePage(Block):
    def __init__(self, message):
        self.message = message
        super().__init__()
    def generate_html(self, request, context=None):
        return (
            f'<title>{self.message}</title></head>'
            f'<body>{self.message}'
        )

class MozumderHTMLMessageTemplate(MozumderTemplate):
    def __init__(self, message):
        self.blocks = [MessagePage(message)]
        super().__init__()

templates_map = {}
templates_map[100] = MozumderHTMLMessageTemplate(
    "100 Continue")
templates_map[101] = MozumderHTMLMessageTemplate(
    "101 Switching Protocols")
templates_map[102] = MozumderHTMLMessageTemplate(
    "102 Processing")
templates_map[103] = MozumderHTMLMessageTemplate(
    "103 Early Hints")
templates_map[200] = MozumderHTMLMessageTemplate(
    "200 OK")
templates_map[201] = MozumderHTMLMessageTemplate(
    "201 Created")
templates_map[202] = MozumderHTMLMessageTemplate(
    "202 Accepted")
templates_map[203] = MozumderHTMLMessageTemplate(
    "203 Non-Authoritative Information")
templates_map[204] = MozumderHTMLMessageTemplate(
    "204 No Content")
templates_map[205] = MozumderHTMLMessageTemplate(
    "205 Reset Content")
templates_map[206] = MozumderHTMLMessageTemplate(
    "206 Partial Content")
templates_map[207] = MozumderHTMLMessageTemplate(
    "207 Multi-Status")
templates_map[208] = MozumderHTMLMessageTemplate(
    "208 Already Reported")
templates_map[226] = MozumderHTMLMessageTemplate(
    "226 IM Used")
templates_map[300] = MozumderHTMLMessageTemplate(
    "300 Multiple Choices")
templates_map[301] = MozumderHTMLMessageTemplate(
    "301 Moved Permanently")
templates_map[302] = MozumderHTMLMessageTemplate(
    "302 Found")
templates_map[303] = MozumderHTMLMessageTemplate(
    "303 See Other")
templates_map[304] = MozumderHTMLMessageTemplate(
    "304 Not Modified")
templates_map[305] = MozumderHTMLMessageTemplate(
    "305 Use Proxy")
templates_map[306] = MozumderHTMLMessageTemplate(
    "306 Switch Proxy")
templates_map[307] = MozumderHTMLMessageTemplate(
    "307 Temporary Redirect")
templates_map[308] = MozumderHTMLMessageTemplate(
    "308 Permanent Redirect")
templates_map[400] = MozumderHTMLMessageTemplate(
    "400 Bad Request")
templates_map[401] = MozumderHTMLMessageTemplate(
    "401 Unauthorized")
templates_map[402] = MozumderHTMLMessageTemplate(
    "402 Payment Required")
templates_map[403] = MozumderHTMLMessageTemplate(
    "403 Forbidden")
templates_map[404] = MozumderHTMLMessageTemplate(
    "404 Not Found")
templates_map[405] = MozumderHTMLMessageTemplate(
    "405 Unauthorized")
templates_map[406] = MozumderHTMLMessageTemplate(
    "406 Not Acceptable")
templates_map[407] = MozumderHTMLMessageTemplate(
    "407 Proxy Authorization Required")
templates_map[408] = MozumderHTMLMessageTemplate(
    "408 Request Timeout")
templates_map[409] = MozumderHTMLMessageTemplate(
    "409 Conflict")
templates_map[410] = MozumderHTMLMessageTemplate(
    "410 Gone")
templates_map[411] = MozumderHTMLMessageTemplate(
    "411 Length Required")
templates_map[412] = MozumderHTMLMessageTemplate(
    "412 Precondition Failed")
templates_map[413] = MozumderHTMLMessageTemplate(
    "413 Payload Too Large")
templates_map[414] = MozumderHTMLMessageTemplate(
    "414 URI Too Long")
templates_map[415] = MozumderHTMLMessageTemplate(
    "415 Unsupported Media Type")
templates_map[416] = MozumderHTMLMessageTemplate(
    "416 Range Not Satisfiable")
templates_map[417] = MozumderHTMLMessageTemplate(
    "417 Expectation Failed")
templates_map[418] = MozumderHTMLMessageTemplate(
    "418 I'm a teapot")
templates_map[421] = MozumderHTMLMessageTemplate(
    "421 Misdirected Request")
templates_map[422] = MozumderHTMLMessageTemplate(
    "422 Unprocessable Entity")
templates_map[423] = MozumderHTMLMessageTemplate(
    "423 Locked")
templates_map[424] = MozumderHTMLMessageTemplate(
    "424 Failed Dependency")
templates_map[426] = MozumderHTMLMessageTemplate(
    "426 Upgrade Required")
templates_map[428] = MozumderHTMLMessageTemplate(
    "428 Precondition Required")
templates_map[429] = MozumderHTMLMessageTemplate(
    "429 Too Many Requests")
templates_map[431] = MozumderHTMLMessageTemplate(
    "431 Request Header Fields Too Large")
templates_map[451] = MozumderHTMLMessageTemplate(
    "451 Unavailable For Legal Reasons")
templates_map[500] = MozumderHTMLMessageTemplate(
    "500 Internal Server Error")
templates_map[501] = MozumderHTMLMessageTemplate(
    "501 Not Implemented")
templates_map[502] = MozumderHTMLMessageTemplate(
    "502 Bad Gateway")
templates_map[503] = MozumderHTMLMessageTemplate(
    "503 Service Unavailable")
templates_map[504] = MozumderHTMLMessageTemplate(
    "504 Gateway Timeout")
templates_map[505] = MozumderHTMLMessageTemplate(
    "505 HTTP Version Not Supported")
templates_map[506] = MozumderHTMLMessageTemplate(
    "506 Variant Also Negotiates")
templates_map[507] = MozumderHTMLMessageTemplate(
    "507 Insufficient Storage")
templates_map[508] = MozumderHTMLMessageTemplate(
    "508 Loop Detected")
templates_map[510] = MozumderHTMLMessageTemplate(
    "510 Not Extended")
templates_map[511] = MozumderHTMLMessageTemplate(
    "511 Network Authentication Required")
