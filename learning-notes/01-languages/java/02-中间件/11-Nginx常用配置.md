# Nginx常用配置
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang
### 代理静态文件

~~~sh 
server {
        listen       10086;
        server_name  localhost;
	
		location / {
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $http_host;
		proxy_set_header X-NginX-Proxy true;
		proxy_redirect off;
		}
		
		location /data/ {
		    alias '/usr/local/data'; 
            //这里是重点，就是代理这个文件夹 , 访问 http://localhost:10086/data/下面的资源就是访问/usr/local/data文件夹的资源
            expires    7d;
        }
}
~~~

### 反向代理
```sh 
server {
    listen       80;
    server_name  www.123.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        index  index.html index.htm index.jsp;
    }
}
```

### 负载均衡
```sh 
http{
    # 待选服务器列表
    upstream myproject{
        # ip_hash指令，将同一用户引入同一服务器。
        ip_hash;
        server 125.219.42.4 fail_timeout=60s;
        server 172.31.2.183;
     }
    server{
        # 监听端口
        listen 80;
        # 根目录下
        location / {
            # 选择哪个服务器列表
            proxy_pass http://myproject;
        }

    }
}
```

### 跨域配置
```sh 
server {
        listen       80;
        server_name  test.cross.com;

	if ( $host ~ (.*).cross.com){
		set $domain $1;##记录二级域名值
	}
	#是否允许请求带有验证信息
	add_header Access-Control-Allow-Credentials true;
	#允许跨域访问的域名,可以是一个域的列表，也可以是通配符*
	add_header Access-Control-Allow-Origin  http://static.enjoy.com;
	#允许脚本访问的返回头
	add_header Access-Control-Allow-Headers 'x-requested-with,content-type,Cache-Control,Pragma,Date,x-timestamp';
	#允许使用的请求方法，以逗号隔开
	add_header Access-Control-Allow-Methods 'POST,GET,OPTIONS,PUT,DELETE';
	#允许自定义的头部，以逗号隔开,大小写不敏感
	add_header Access-Control-Expose-Headers 'WWW-Authenticate,Server-Authorization';
	#P3P支持跨域cookie操作
	add_header P3P 'policyref="/w3c/p3p.xml", CP="NOI DSP PSAa OUR BUS IND ONL UNI COM NAV INT LOC"';
	if ($request_method = 'OPTIONS') {##OPTIONS类的请求，是跨域先验请求
            return 204;##204代表ok
        }
}
```
### 资源压缩
```sh 
location ~ /(.*)\.(html|js|css|png)$ {
    gzip on; # 启用gzip压缩，默认是off，不启用
    # 对js、css、jpg、png、gif格式的文件启用gzip压缩功能
    gzip_types application/javascript text/css Nginx-image/jpeg Nginx-image/png Nginx-image/gif;
    gzip_min_length 1024; # 所压缩文件的最小值，小于这个的不会压缩
    gzip_buffers 4 1k; # 设置压缩响应的缓冲块的大小和个数，默认是内存一个页的大小
    gzip_http_version 1.0;
    gzip_vary off;
    gzip_comp_level 1; # 压缩水平，默认1。取值范围1-9，取值越大压缩比率越大，但越耗cpu时间
    root /etc/nginx/html/gzip;
}
```
### 防盗链
```sh 
# 需要防盗的后缀
location ~* \.(jpg|jpeg|png|gif|bmp|swf|rar|zip|doc|xls|pdf|gz|bz2|mp3|mp4|flv)$
    #设置过期时间
    expires     30d;
    # valid_referers 就是白名单的意思
    # 支持域名或ip
    # 允许ip 192.168.0.1 的请求
    # 允许域名 *.google.com 所有子域名
    valid_referers none blocked 192.168.0.1 *.google.com;
    if ($invalid_referer) {
        # return 403;
        # 盗链返回的图片，替换盗链网站所有盗链的图片
        rewrite ^/ https://site.com/403.jpg;
    }
    root  /usr/share/nginx/img;
}
```
> 以上配置主要看 valid_referers，这个变量代表只允许网址访问，上面配置中允许 IP 为 192.168.0.1 和 Google 搜索引擎访问图片该服务下的资源，否则就重定向到一张默认图片

### 配置SSL
#### 申请证书
​ 在这里，我直接申请腾讯云的免费证书。这里需要注意下，这亚洲诚信机构颁发的免费证书只能一个域名使用，子域名那些需要另外申请。别说，这腾讯里面申请还挺快的，十多分钟就通过了。下载的是一个zip文件，解压后打开里面的Nginx文件夹，把1_XXX.com_bundle.crt跟2_XXX.com.key文件复制下来。

#### 查看配置文件
```sh 
# 运行用户，默认即是nginx，可以不进行设置
user  nginx;
#Nginx进程，一般设置为和CPU核数一样
worker_processes  1;

#错误日志存放目录
error_log  /var/log/nginx/error.log warn;
#进程pid存放位置
pid        /var/run/nginx.pid;

events {
    worker_connections  1024; # 单个后台进程的最大并发数
}

http {
    include       /etc/nginx/mime.types; #文件扩展名与类型映射表
    default_type  application/octet-stream; #默认文件类型
    #设置日志模式
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main; #nginx访问日志存放位置

    sendfile        on; #开启高效传输模式
    #tcp_nopush     on; #减少网络报文段的数量

    keepalive_timeout  65; #保持连接的时间，也叫超时时间

    #gzip  on; #开启gzip压缩

    include /etc/nginx/conf.d/*.conf; #包含的子配置项位置和文件
}
```
> 这是全局配置。为了更好管理，我们还是在最后一行声明的/etc/nginx/conf.d文件夹里进行子项目配置。

#### 修改default.conf
> 打开里面的default.conf

```sh
http{
    #http节点中可以添加多个server节点
    server{
        #监听443端口
        listen 443;
        #对应的域名，baiyp.com改成你们自己的域名就可以了
        server_name baiyp.com;
        ssl on;
        #从腾讯云获取到的第一个文件的全路径
        ssl_certificate /etc/ssl/1_baofeidyz.com_bundle.crt;
        #从腾讯云获取到的第二个文件的全路径
        ssl_certificate_key /etc/ssl/2_baofeidyz.com.key;
        ssl_session_timeout 5m;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
        ssl_prefer_server_ciphers on;
        #这是我的主页访问地址，因为使用的是静态的html网页，所以直接使用location就可以完成了。
        location / {
                #文件夹
                root /usr/local/service/ROOT;
                #主页文件
                index index.html;
        }
    }
    server{
        listen 80;
        server_name baofeidyz.com;
        rewrite ^/(.*)$ https://baofeidyz.com:443/$1 permanent;
    }

}
```
> 重启后就可以测试了
