from urllib.parse import urlparse
import socket
import sys, getopt

def createZone(inp, out):
    out = open(out, 'w')
    out.write("$TTL 60s;\n$ORIGIN ua.\n@          SOA dns.ua. ung.utt.fr ( 1 20m 15m 1d 2h)\n           NS dns.ua.\n\n")
    with open(inp) as f:
        lines = f.readlines()
        cpt = 0
        for line in lines:
            p = urlparse(line)
            h = p.hostname
            if h is not None:
                try:
                    socket.inet_aton(h)
                except socket.error:
                    cpt += 1
                    out.write("%s   CNAME .\n" % h)
        print("%d lines in zonefile." % cpt)
    out.close()

def printHelp():
    print('createRpz.py -i <inputfile> -o <outputfile>')

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      printHelp()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         printHelp()
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   if inputfile == '' or outputfile == '':
       printHelp()
   else:
       createZone(inputfile, outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])