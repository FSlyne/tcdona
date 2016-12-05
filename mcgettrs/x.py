from ona.pronto import *
pronto=Pronto('10.10.10.11')
pronto.sendcmd('bash /home/tcdonalab2.sh')
pronto.sendcmd('bash /home/tcdonalab2_redpath.sh')
pronto.sendcmd('bash /home/tcdonalab2_greenpath.sh')

