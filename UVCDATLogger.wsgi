import socket,hashlib,MySQLdb
def initdb(cur):
  users="""CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `md5` varchar(32) DEFAULT NULL,
  `machine` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`))"""
  domains = """ CREATE TABLE `domains` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `ip1` int DEFAULT NULL,
  `ip2` int DEFAULT NULL,
  PRIMARY KEY (`id`)
)"""
  machines = """ CREATE TABLE `machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `md5` varchar(32) DEFAULT NULL,
  `domain` int(11) DEFAULT NULL,
  `platform` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
)"""
  sources = """ CREATE TABLE `sources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`id`)
)"""
  actions = """ CREATE TABLE `actions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(12) DEFAULT NULL,
  PRIMARY KEY (`id`)
)"""
  access = """ CREATE TABLE `access` (
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` int(11) DEFAULT NULL,
  `source` int(11) DEFAULT NULL,
  `action` int(11) DEFAULT NULL
)"""

  ## drop tables
  cur.execute("drop table if exists domains")
  cur.execute("drop table if exists users")
  cur.execute("drop table if exists sources")
  cur.execute("drop table if exists actions")
  cur.execute("drop table if exists machines")
  cur.execute("drop table if exists access")

  ## recreate tables
  cur.execute(domains)
  cur.execute(users)
  cur.execute(sources)
  cur.execute(actions)
  cur.execute(machines)
  cur.execute(access)

  return 

def application(environ,start_response):
   start_response("200 OK",[("Content-type","text/html")])
   ip=environ["REMOTE_ADDR"]
   #return [ip,]
   ipsp=ip.split(".")
   ip1=ipsp[0]
   ip2=ipsp[1]
   #return ["IP$$:"+ip,]
   try:
     name = socket.gethostbyaddr(ip)
   except Exception,err:
     name=["Unkwown",[],ip]
   #return [str(name),]
   path = environ["PATH_INFO"]
   try:
     sp=path.split("/")
   except:
     sp=[]
   #return ["OKKK",]
   if len(sp)<2:
     return ["Thanks for your interest"]
   usernm=sp[1]
   platform=sp[2]
   source=sp[3]
   action=sp[4]
   user = hashlib.md5("%s.%s" % (ip,usernm)).hexdigest()
   domain=".".join(name[0].split(".")[-2:])
   #return [domain]
   # Now the mysql stuff
   db=MySQLdb.connect("localhost","uvcdatlogs","uvcdat","uvcdatlogs")
   #return ["db"]
   cur=db.cursor()
   def myexec(cmd):
    try:
     cur.execute(cmd)
     r=cur.fetchall()
    except Exception,err:
     r=err
    return r

   ## Finally store the result, we may want to stop filtering the possible actions
   root="doutriaux1"
   passwd="CDATRocks"
   #return [source,]
   if source=="init":
      if usernm==root and action==passwd:
         r = initdb(cur)
   elif source=="showlog":
      if usernm==root and action==passwd:
         r="<center><table border=1><caption>Domains</caption><tr><th>#</th><th>domain</th><th>ips</th></tr>"
         r1 = myexec("select * from domains order by name ;")
         for R in r1:
           r+="<tr><td>%i</td><td>%s</td><td>%i.%i.x.x</td></tr>" % (R[0],R[1],R[2],R[3])
	 r+="</table><br><table border=1><caption>Log (latest 200 entries)</caption><tr><th>Date</th><th>Domain</th><th>Platform</th><th>Source</th><th>Action</th></tr>"
         r1 = myexec("select * from access order by date desc;")
         for R in r1[:200]:
           platforms=myexec("select platform,domain from machines left join users on machines.id = users.machine where users.id = %i;"% R[1])[0]
	   platform=platforms[0]
	   domain=platforms[1]
	   domain=myexec("select name from domains where id = %i;"% domain)[0][0]
           src=myexec("select name from sources where id = %i;"% R[2])[0][0]
           act=myexec("select name from actions where id = %i;"% R[3])[0][0]
           r+="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (str(R[0]),domain,platform,src,act)
	 r+="</table></center>"
               
   elif  source in ["bldcnf","bldcmk","cdat","uvcdat","search"]:
    ## First checks domain
    cmd = "select * from domains where name = '%s' and ip1 = %s and ip2 = %s;" % (domain,ip1,ip2)
    r = myexec(cmd)
    if len(r)==0:
     r=myexec("insert into domains (name, ip1, ip2) values ('%s', %s, %s);" % (domain,ip1,ip2))
     r=myexec(cmd)
    domain = int(r[0][0])
    ## Second of all check machine
    machine = hashlib.md5(ip).hexdigest()
    cmd = "select * from machines where md5 = '%s';" % machine
    r = myexec(cmd)
    if len(r)==0:
     r=myexec("insert into machines (md5, domain, platform) values ('%s', %i, '%s');" % (machine,domain,platform))
     r = myexec(cmd)
    machine = int(r[0][0])

    ## Now on to  the user
    cmd = "select * from users where md5 = '%s';" % user
    r = myexec(cmd)
    if len(r)==0:
     r=myexec("insert into users (md5, machine) values ('%s', '%i');" % (user,machine))
     r=myexec(cmd)
    user = int(r[0][0])
    ## Source
    cmd = "select * from sources where name = '%s';" % source[:8].strip()
    r = myexec(cmd)
    if len(r)==0:
     r=myexec("insert into sources (name) values ('%s');" % (source[:8]))
     r=myexec(cmd)
    src = int(r[0][0])
    ## Action
    cmd = "select * from actions where name = '%s';" % action[:12].strip()
    r = myexec(cmd)
    if len(r)==0:
     r=myexec("insert into actions (name) values ('%s');" % (action[:12]))
     r=myexec(cmd)
    act = int(r[0][0])
    r=myexec("insert into access (date, user, source, action) values (now(), %i, %i, %i);" % (user,src,act))
   else:
     r="Unknown source"
   return ["%s" % repr(r)]
if __name__=="__main__":
   from wsgiref.simple_server import make_server
   server = make_server('localhost', 8080, application)
   server.serve_forever()
