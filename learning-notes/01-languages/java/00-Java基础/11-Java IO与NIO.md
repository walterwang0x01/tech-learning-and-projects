# Java IO与NIO
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Java IO概述

### 1.1 IO流分类

#### 按数据流向
- **输入流（InputStream/Reader）**：从外部读取数据到程序
- **输出流（OutputStream/Writer）**：从程序写入数据到外部

#### 按数据类型
- **字节流（InputStream/OutputStream）**：以字节为单位读写数据
- **字符流（Reader/Writer）**：以字符为单位读写数据

#### 按功能
- **节点流**：直接操作数据源的流
- **处理流**：对节点流进行包装，提供额外功能

### 1.2 IO流类层次结构

```
InputStream
├── FileInputStream
├── ByteArrayInputStream
├── BufferedInputStream
└── ObjectInputStream

OutputStream
├── FileOutputStream
├── ByteArrayOutputStream
├── BufferedOutputStream
└── ObjectOutputStream

Reader
├── FileReader
├── BufferedReader
├── InputStreamReader
└── StringReader

Writer
├── FileWriter
├── BufferedWriter
├── OutputStreamWriter
└── StringWriter
```

## 2. 字节流

### 2.1 FileInputStream

#### 读取文件

```java
FileInputStream fis = null;
try {
    fis = new FileInputStream("file.txt");
    int data;
    while ((data = fis.read()) != -1) {
        System.out.print((char) data);
    }
} catch (IOException e) {
    e.printStackTrace();
} finally {
    if (fis != null) {
        try {
            fis.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

#### 使用缓冲区读取

```java
try (FileInputStream fis = new FileInputStream("file.txt")) {
    byte[] buffer = new byte[1024];
    int len;
    while ((len = fis.read(buffer)) != -1) {
        System.out.println(new String(buffer, 0, len));
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

### 2.2 FileOutputStream

#### 写入文件

```java
try (FileOutputStream fos = new FileOutputStream("output.txt")) {
    String data = "Hello, World!";
    fos.write(data.getBytes());
} catch (IOException e) {
    e.printStackTrace();
}
```

#### 追加模式

```java
try (FileOutputStream fos = new FileOutputStream("output.txt", true)) {
    String data = "追加内容";
    fos.write(data.getBytes());
} catch (IOException e) {
    e.printStackTrace();
}
```

### 2.3 BufferedInputStream / BufferedOutputStream

提供缓冲功能，提高IO性能。

```java
try (BufferedInputStream bis = new BufferedInputStream(
        new FileInputStream("input.txt"));
     BufferedOutputStream bos = new BufferedOutputStream(
        new FileOutputStream("output.txt"))) {
    
    byte[] buffer = new byte[1024];
    int len;
    while ((len = bis.read(buffer)) != -1) {
        bos.write(buffer, 0, len);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

## 3. 字符流

### 3.1 FileReader / FileWriter

#### 读取文件

```java
try (FileReader fr = new FileReader("file.txt")) {
    int data;
    while ((data = fr.read()) != -1) {
        System.out.print((char) data);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

#### 写入文件

```java
try (FileWriter fw = new FileWriter("output.txt")) {
    fw.write("Hello, World!");
} catch (IOException e) {
    e.printStackTrace();
}
```

### 3.2 BufferedReader / BufferedWriter

提供缓冲功能和按行读取。

```java
try (BufferedReader br = new BufferedReader(
        new FileReader("file.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

#### 写入文件

```java
try (BufferedWriter bw = new BufferedWriter(
        new FileWriter("output.txt"))) {
    bw.write("第一行");
    bw.newLine();
    bw.write("第二行");
} catch (IOException e) {
    e.printStackTrace();
}
```

### 3.3 InputStreamReader / OutputStreamWriter

字节流和字符流之间的桥梁。

```java
try (InputStreamReader isr = new InputStreamReader(
        new FileInputStream("file.txt"), "UTF-8")) {
    int data;
    while ((data = isr.read()) != -1) {
        System.out.print((char) data);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

## 4. 对象流

### 4.1 ObjectInputStream / ObjectOutputStream

用于序列化和反序列化对象。

```java
// 序列化
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("object.dat"))) {
    User user = new User("张三", 25);
    oos.writeObject(user);
} catch (IOException e) {
    e.printStackTrace();
}

// 反序列化
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("object.dat"))) {
    User user = (User) ois.readObject();
    System.out.println(user);
} catch (IOException | ClassNotFoundException e) {
    e.printStackTrace();
}
```

**注意**：被序列化的类必须实现`Serializable`接口。

## 5. NIO概述

### 5.1 NIO vs IO

| 特性 | IO | NIO |
|------|----|-----|
| 工作方式 | 阻塞IO | 非阻塞IO |
| 缓冲区 | 无 | 有（Buffer） |
| 选择器 | 无 | 有（Selector） |
| 适用场景 | 连接数少 | 连接数多 |

### 5.2 NIO核心组件

- **Channel（通道）**：数据的双向传输通道
- **Buffer（缓冲区）**：数据的临时存储区
- **Selector（选择器）**：多路复用器

## 6. Buffer

### 6.1 Buffer的基本使用

```java
ByteBuffer buffer = ByteBuffer.allocate(1024);

// 写入数据
buffer.put("Hello".getBytes());

// 切换到读模式
buffer.flip();

// 读取数据
while (buffer.hasRemaining()) {
    System.out.print((char) buffer.get());
}

// 清空缓冲区
buffer.clear();
```

### 6.2 Buffer的三个重要属性

- **position**：当前位置
- **limit**：限制位置
- **capacity**：容量

### 6.3 Buffer的常用方法

```java
ByteBuffer buffer = ByteBuffer.allocate(1024);

buffer.put(data);        // 写入数据
buffer.flip();          // 切换到读模式
buffer.get();           // 读取数据
buffer.rewind();        // 重新读取
buffer.clear();         // 清空缓冲区
buffer.compact();       // 压缩缓冲区
buffer.mark();          // 标记位置
buffer.reset();         // 重置到标记位置
```

## 7. Channel

### 7.1 FileChannel

#### 读取文件

```java
try (FileChannel channel = new FileInputStream("file.txt").getChannel()) {
    ByteBuffer buffer = ByteBuffer.allocate(1024);
    while (channel.read(buffer) != -1) {
        buffer.flip();
        while (buffer.hasRemaining()) {
            System.out.print((char) buffer.get());
        }
        buffer.clear();
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

#### 写入文件

```java
try (FileChannel channel = new FileOutputStream("output.txt").getChannel()) {
    ByteBuffer buffer = ByteBuffer.wrap("Hello, World!".getBytes());
    channel.write(buffer);
} catch (IOException e) {
    e.printStackTrace();
}
```

#### 文件复制

```java
try (FileChannel source = new FileInputStream("source.txt").getChannel();
     FileChannel dest = new FileOutputStream("dest.txt").getChannel()) {
    dest.transferFrom(source, 0, source.size());
} catch (IOException e) {
    e.printStackTrace();
}
```

### 7.2 SocketChannel

#### 客户端

```java
SocketChannel channel = SocketChannel.open();
channel.connect(new InetSocketAddress("localhost", 8080));

ByteBuffer buffer = ByteBuffer.wrap("Hello".getBytes());
channel.write(buffer);

channel.close();
```

#### 服务端

```java
ServerSocketChannel serverChannel = ServerSocketChannel.open();
serverChannel.bind(new InetSocketAddress(8080));
serverChannel.configureBlocking(false);

Selector selector = Selector.open();
serverChannel.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select();
    Set<SelectionKey> keys = selector.selectedKeys();
    Iterator<SelectionKey> iter = keys.iterator();
    
    while (iter.hasNext()) {
        SelectionKey key = iter.next();
        iter.remove();
        
        if (key.isAcceptable()) {
            ServerSocketChannel server = (ServerSocketChannel) key.channel();
            SocketChannel client = server.accept();
            client.configureBlocking(false);
            client.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            SocketChannel client = (SocketChannel) key.channel();
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            client.read(buffer);
            buffer.flip();
            // 处理数据
        }
    }
}
```

## 8. Selector

### 8.1 Selector的使用

```java
Selector selector = Selector.open();

// 注册通道
channel.configureBlocking(false);
SelectionKey key = channel.register(selector, SelectionKey.OP_READ);

// 选择就绪的通道
int readyChannels = selector.select();

if (readyChannels == 0) {
    return;
}

Set<SelectionKey> selectedKeys = selector.selectedKeys();
Iterator<SelectionKey> keyIterator = selectedKeys.iterator();

while (keyIterator.hasNext()) {
    SelectionKey key = keyIterator.next();
    
    if (key.isAcceptable()) {
        // 连接就绪
    } else if (key.isConnectable()) {
        // 连接完成
    } else if (key.isReadable()) {
        // 读就绪
    } else if (key.isWritable()) {
        // 写就绪
    }
    
    keyIterator.remove();
}
```

### 8.2 SelectionKey

- **OP_ACCEPT**：接受连接就绪
- **OP_CONNECT**：连接就绪
- **OP_READ**：读就绪
- **OP_WRITE**：写就绪

## 9. NIO.2（Java 7+）

### 9.1 Path

```java
Path path = Paths.get("file.txt");
Path absolutePath = path.toAbsolutePath();
Path parent = path.getParent();
String fileName = path.getFileName().toString();
```

### 9.2 Files

#### 读取文件

```java
// 读取所有行
List<String> lines = Files.readAllLines(Paths.get("file.txt"));

// 读取所有字节
byte[] bytes = Files.readAllBytes(Paths.get("file.txt"));

// 按行读取
Files.lines(Paths.get("file.txt")).forEach(System.out::println);
```

#### 写入文件

```java
// 写入字符串
Files.write(Paths.get("output.txt"), "Hello".getBytes());

// 写入多行
List<String> lines = Arrays.asList("line1", "line2");
Files.write(Paths.get("output.txt"), lines);
```

#### 文件操作

```java
// 复制文件
Files.copy(source, dest, StandardCopyOption.REPLACE_EXISTING);

// 移动文件
Files.move(source, dest, StandardCopyOption.REPLACE_EXISTING);

// 删除文件
Files.delete(path);

// 检查文件是否存在
boolean exists = Files.exists(path);
```

### 9.3 AsynchronousFileChannel

异步文件操作。

```java
AsynchronousFileChannel channel = AsynchronousFileChannel.open(
    Paths.get("file.txt"), StandardOpenOption.READ);

ByteBuffer buffer = ByteBuffer.allocate(1024);

channel.read(buffer, 0, null, new CompletionHandler<Integer, ByteBuffer>() {
    @Override
    public void completed(Integer result, ByteBuffer attachment) {
        System.out.println("读取完成：" + result);
    }
    
    @Override
    public void failed(Throwable exc, ByteBuffer attachment) {
        exc.printStackTrace();
    }
});
```

## 10. IO vs NIO选择

### 10.1 使用IO的场景

- 连接数较少
- 需要阻塞式编程模型
- 简单的文件操作

### 10.2 使用NIO的场景

- 连接数较多
- 需要非阻塞IO
- 需要高性能网络编程

## 11. 最佳实践

1. **使用try-with-resources**：自动关闭资源
2. **使用缓冲流**：提高IO性能
3. **合理选择IO/NIO**：根据场景选择
4. **处理异常**：正确捕获和处理IO异常
5. **关闭资源**：确保资源被正确关闭

## 12. 性能优化

1. **使用缓冲**：BufferedInputStream、BufferedReader等
2. **批量读写**：使用数组批量读写数据
3. **NIO零拷贝**：使用FileChannel.transferTo/transferFrom
4. **异步IO**：使用AsynchronousFileChannel提高性能

