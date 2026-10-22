path = r'G:\\Games\\CnMod 1.2\\.ai\\scripts\\modkit.py'
s = open(path,'r',encoding='utf-8').read()
m = '    p_cg.add_argument("--to", dest="to_id", required=True)\n\n    args = ap.parse_args(argv)'
inj = '''    p_cg.add_argument("--to", dest="to_id", required=True)

    p_th = sub.add_parser("template-house", help="szablon domu")
    p_th.add_argument("--id", dest="id", required=True)
    p_tg = sub.add_parser("template-good", help="szablon surowca")
    p_tg.add_argument("--id", dest="id", required=True)

    args = ap.parse_args(argv)'''
if m in s:
    s = s.replace(m, inj)
m2 = '    if args.cmd == "clone-good":\n        return clone_good(root, cif2txt, args)\n    return 2'
inj2 = '''    if args.cmd == "clone-good":
        return clone_good(root, cif2txt, args)
    if args.cmd == "template-house":
        return cmd_template_house(root, cif2txt, args)
    if args.cmd == "template-good":
        return cmd_template_good(root, cif2txt, args)
    return 2'''
if m2 in s:
    s = s.replace(m2, inj2)
open(path,'w',encoding='utf-8').write(s)
print('ok')
