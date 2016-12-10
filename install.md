# Lancache UTT Arena

Faute d'espace de doc dédié à l'UA, cette page va ici.
Elle présente des infos succinctes sur l'installation d'une machine de LanCache, afin d'éviter de rechercher la conf tous les ans.
L'objectif d'un LanCache est de mettre en cache local des fichiers d'install / MaJ de jeux en réseaux, i.e. de les télécharger une fois puis de les servir en local, afin d'éviter de saturer les liens externes avec des DL de jeux.

Les fichiers de configurations, scripts pertinents, ainsi que le présent guide se trouvent sur un dépôt Git. Merci de le cloner quelque part : `git clone --URL repo UNG--`

## Hardware / Optis OS / FS

Voir avec T. Chauchefoin.

## Logiciel

### Firewall

Le cas échéant, commencez par désactiver les règles ipTables interdisant les connexions HTTP à la machine (probable si sous CentOS). Un script _ad hoc_ est disponible dans le dépôt (cf. supra), fichier `fw_stop.sh`.

### Compiler NginX

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

### Config LanCache

Copiez ensuite les fichiers pertinents depuis le dépôt dans le répertoire de conf Nginx (/etc/nginx) :
  * lancache
  * machines
  * nginx.conf
  * sites
  * vhosts

Vérifiez la config (`service nginx configtest`) et, si tout est bon, rechargez la config (`service nginx reload`).
