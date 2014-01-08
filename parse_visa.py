#!/usr/bin/env python
# coding: utf-8

import sys
import os
import re
from subprocess import call
import random
import string

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def _parse(text_file):
    resumen = open(text_file, 'r').read()
    beg = resumen.find("DETALLE DE TRANSACCION")
    end = resumen.find("LA SUMA DE")
    if not beg or not end:
        return
    resumen = resumen[beg:end]
    content_ars = ""
    content_usd = ""
    content_cuotas = ""
    for line in resumen.split("\n"):
        line = line.strip()
        if line:
            date = re.search(r'(\d{2}\.\d{2}\.\d{2})', line)
            if date:
                date = date.group()
                date = date.replace(".", "-")
            else:
                continue

            code = re.search(r'\d{6}', line)
            if code:
                code = code.group()
            else:
                continue
            
            line_parts = line[10:].split(" ")
            amount = line_parts.pop(-1)
            
            item = line[26:100].strip()
            #print date, code, item, amount

            if "EUR" in line or "USD" in line:
                content_usd += '\t'.join([date, code, item, "USD", amount]) + "\n"
            elif "Cuota" in line:
                content_cuotas += '\t'.join([date, code, item, "USD", amount]) + "\n"
            else:
                content_ars += '\t'.join([date, code, item, "ARS", amount]) + "\n"
            
    return content_ars, content_usd, content_cuotas

def main(argv):
    if len(argv) < 2:
        print "Please supply input and output file"
        return
    if os.path.exists(argv[1] + "_ars.txt") or os.path.exists(argv[1] + "_usd.txt") \
    or os.path.exists(argv[1] + "_cuotas.txt"):
        print "Output file already exists."
        return
        
    temp_textfile = id_generator() + ".txt"
    call(["pdftotext", argv[0], "-layout", temp_textfile])
    if not os.path.exists(temp_textfile):
        print "Error converting pdf."
        return
    try:
        res_ars, res_usd, res_cuotas = _parse(temp_textfile)
    except Exception, e:
        print e
    finally:
        os.remove(temp_textfile)
    
    with open(argv[1] + "_ars.txt", "w") as f:
        f.write(res_ars)
    
    with open(argv[1] + "_usd.txt", "w") as f:
        f.write(res_usd)
    
    with open(argv[1] + "_cuotas.txt", "w") as f:
        f.write(res_cuotas)

if __name__ == "__main__":
    main(sys.argv[1:])
