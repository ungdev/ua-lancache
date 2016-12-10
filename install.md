# Lancache UTT Arena

L'objectif d'un LanCache est de mettre en cache local des fichiers d'install / MaJ de jeux en réseaux, i.e. de les télécharger une fois puis de les servir en local, afin d'éviter de saturer les liens externes avec des DL de jeux.

Les fichiers de configurations, scripts pertinents, ainsi que le présent guide se trouvent sur un dépôt Git. Merci de le cloner quelque part : `git clone git@github.com:ungdev/ua-lancache.git`

## Réseau

Configurez une IP classique sur l'interface principale de la machine (ici 10.50.0.1), et 6 IPs virtuelles (10.50.0.3-8 en 2016). Celles-ci devront être résolues avec le nom d'hôte donné dans la config du cache, afin de permettre l'interception correcte des NDD sans SNI par Nginx.

## Firewall

Le cas échéant, commencez par désactiver les règles ipTables interdisant les connexions HTTP à la machine (probable si sous CentOS). Un script _ad hoc_ est disponible dans le dépôt (cf. supra), fichier `fw_stop.sh`.

## DNS

Un récurseur DNS compatible RPZ (cf. [RFC draft-vixie-dns-rpz-00](https://tools.ietf.org/html/draft-vixie-dns-rpz-00)) est requis : en effet, le LanCache doit pouvoir intercepter toute requête de DL à destination des CDN des éditeurs. Par conséquent, ce serveur doit être adopté par tous les joueurs. Il est recommandé de le pousser par DHCP, et de bloquer le trafic sur le port 53 vers toute autre machine.  
Nous suggérons [PowerDNS](https://www.powerdns.com/), à installer depuis leurs dépôts ([instructions](https://repo.powerdns.com/)). Vous pouvez également installer le serveur d'autorité, afin de gérer la résolution des noms à l'UA.  
A cet effet, les fichiers de config associés sont dans le répertoire `dns` du dépôt. Le serveur d'autorité est configuré pour écouter sur le port 53, répondre à toute requête pur laquelle il fait autorité, et sinon la transférer au récurseur sur le port 8953, qui loade les zones RPZ spécifiées dans son fichier de configuration additionnelle LUA, renvoie la réponse-mensonge si elle existe, sinon effectue une récursion normale.  
En outre, nous proposons également une zone RPZ avec quelques trackers torrent, afin de limiter l'utilisation de BW. Vous pouvez la regénérer à partir d'une liste d'URL tracker de votre choix, *via* le script python dans `dns/createRpz.py`

## Compiler NginX

Installez les paquets requis pour la compilation :
`yum -y install gcc gcc-c++ make zlib-devel pcre-devel openssl-devel`

  - Récupérer les [sources](http://nginx.org/en/download.html) de la dernière version
  - Récupérer les [sources](http://labs.frickle.com/nginx_ngx_cache_purge/) du module ngx_cache_purge
  - Décompressez les quelque part (e.g. /tmp)

Collez dans un fichier le script de configuration suivant :
```bash
./configure --user=nginx --group=nginx --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --conf-path=/etc/nginx/nginx.conf --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --with-http_gzip_static_module --with-http_stub_status_module --with-http_ssl_module --with-pcre --with-file-aio --with-http_realip_module --without-http_scgi_module --without-http_uwsgi_module --without-http_fastcgi_module --add-module=../ngx_cache_purge-2.3
```
Note: la config nécessite normalement le module range_cache, qui n'existe pas encore. On le remplace par le module slice.

Rendez-le exécutable, lancez-le, vérifiez que tout est bon, sinon réparez les problèmes (vérifiez bien les dépendances ci-dessus. Puis :
```bash
make
make install
```

Ajoutez l'utilisateur et le groupe `nginx` au système, puis lancez les commandes suivantes pour installer le service système :
```bash
wget -O /etc/init.d/nginx https://gist.github.com/sairam/5892520/raw/b8195a71e944d46271c8a49f2717f70bcd04bf1a/etc-init.d-nginx
chmod +x /etc/init.d/nginx
chkconfig --add nginx
chkconfig --level 345 nginx on
service nginx start
```

## Config LanCache

Copiez ensuite les fichiers pertinents depuis le dépôt dans le répertoire de conf Nginx (/etc/nginx) :
  * lancache
  * machines
  * nginx.conf
  * sites
  * vhosts

Vérifiez la config (`service nginx configtest`) et, si tout est bon, rechargez la config (`service nginx reload`).
