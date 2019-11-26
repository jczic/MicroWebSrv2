
![New microWebSrv2](/img/microWebSrv2.png "microWebSrv2")

<br />

![Release](https://img.shields.io/github/v/release/jczic/microwebsrv2?include_prereleases&color=success)
![Size](https://img.shields.io/github/languages/code-size/jczic/microwebsrv2?color=blue)
![MicroPython](https://img.shields.io/badge/micropython-Ok-green.svg)
![Python](https://img.shields.io/badge/python-Ok-green.svg)
![License](https://img.shields.io/github/license/jczic/microwebsrv2?color=yellow)

<br />

**MicroWebSrv2** is the new powerful embedded Web Server for **MicroPython** and **CPython** that supports **route handlers**, modules like **WebSockets** or **PyhtmlTemplate** and a **lot of simultaneous requests** (in thousands!).

**Fully asynchronous**, its connections and memory management are **very optimized** and **truly fast**.

Mostly used on **Pycom WiPy**, **ESP32**, **STM32** on **Pyboard**, ... **Robust** and **efficient**! (see [Features](#features))

#### [Download the latest version (Zip)](https://github.com/jczic/MicroWebSrv2/archive/master.zip)

<br />

---

```sh
                _               __    __     _     __            ____  
      _ __ ___ (_) ___ _ __ ___/ / /\ \ \___| |__ / _\_ ____   _|___ \ 
     | '_ ` _ \| |/ __| '__/ _ \ \/  \/ / _ | '_ \\ \| '__\ \ / / __) |
     | | | | | | | (__| | | (_) \  /\  |  __| |_) _\ | |   \ V / / __/ 
     |_| |_| |_|_|\___|_|  \___/ \/  \/ \___|_.__/\__|_|    \_/ |_____|  JC`zic & HC²


```

---

<br />

# Table of contents

- [**About**](#about)
- [**Features**](#features)
- [**Install**](#install)
- [**Demo**](#demo)
- [**Usage**](#usage)
- [**Documentation**](#documentation)
  - [**MicroWebSrv2 package**](#mws2-package)
  - [**Working with microWebSrv2**](#working-with-mws2)
    - [Asynchronous logic](#async-logic)
    - [Configuring web server](#config-web-srv)
      - [Default pages](#default-pages)
      - [MIME types](#mime-types)
    - [Starting web server](#start-web-srv)
    - [Handling web routes](#handling-routes)
    - [SSL/TLS security (HTTPS)](#ssl-security)
  - [**About XAsyncSockets layer**](#xasyncsockets)
  - [**MicroWebSrv2 Class**](#mws2-class)
    - [Static Methods](#mws2-static-func)
    - [Instance Methods](#mws2-func)
    - [Properties](#mws2-prop)
  - [**Web Routes**](#web-routes)
    - [Route Processing](#route-process)
    - [Route Arguments](#route-args)
    - [Route Methods](#route-func)
  - [**HttpRequest Class**](#request-class)
    - [Instance Methods](#request-func)
    - [Properties](#request-prop)
  - [**HttpResponse Class**](#response-class)
    - [Instance Methods](#response-func)
    - [Properties](#response-prop)
  - [**Additional modules**](#modules)
    - [**WebSockets Module**](#websockets-mod)
      - [Properties](#websockets-mod-prop)
      - [WebSocket Class](#websocket-class)
        - [Instance Methods](#websocket-func)
        - [Properties](#websocket-prop)
    - [**PyhtmlTemplate Module**](#pyhtmltemplate-mod)
      - [Instance Methods](#pyhtmltemplate-func)
      - [Properties](#pyhtmltemplate-prop)
- [**Author**](#author)
- [**License**](#license)

---

<a name="about"></a>
# About

This project follows the embedded [MicroWebSrv](https://github.com/jczic/MicroWebSrv),
which is mainly used on microcontrollers such as Pycom, ESP32 and STM32 on Pyboards.

In a need for scalability and to meet the IoT universe, **microWebSrv2** was developed as a new project
and has been completely redesigned to be much more robust and efficient that its predecessor.

Internal mechanisms works **directly at I/O level**, are fully asynchronous from end to end, and manages the memory in a highly optimized way.  
Also, architecture makes its integration very easy and the source code, **MIT licensed**, remains really small.

---

<a name="features"></a>
# Features

- Embed **microWebSrv2** into your microcontrollers as a **powerful web server**.

- Benefit from a fully **asynchronous architecture** that allows to process many **concurrent requests** very quickly.

- Use multiple worker threads to **parallelize simultaneous processes**.

- Adjust settings to **fine-tune resources usage** and sizing pre-allocated memory.

- Load **additional modules** to extend the server's functionalities.

- Customize the management of **centralized logs**.

- Apply **SSL/TLS security layer** and certificate on web connections (https mode).

- Define **web routes** with variable arguments in order to be able to process the targeted requests.

- Receive any type of request such as ```GET```, ```HEAD```, ```POST```, ```PUT```, ```DELETE```, ```OPTIONS```, ```PATCH```, ...

- Use the **route resolver** (from the path) and the **path builder** (from the route) for convenience.

- Increase loading speed by automatically allowing web clients to **cache static files**.

- Receive name/value pairs from **URL encoded forms**.

- Send and receive **JSON** objects and use them to create a **RESTful API** style.

- Play with **AjAX** requests to interact quickly with a web application.

- Define the **origin** of resources and allow all values of **CORS** pre-flight requests.

- Verify that a request is successfully **authenticated** by the **Basic** or **Bearer** method.

- Reduce the number of persistent connections per web client with **keep-alive mode** support.

- Respond to a request by using a **data stream** as content, sent with known length or in **chunked transfer-encoding**.

- Use a file to respond to a request that will be treated as **on-the-fly content** or as an **attachment to download**.

- Take advantage of the **WebSockets module** to exchange messages in real time via **WS or secured WSS** connection.

- Create **.pyhtml pages** for an HTML rendering with integrated Python using the **PyhtmlTemplate module**.

---

<a name="install"></a>
# Install

- **Solution 1**, clone the [GitHub repository](https://github.com/jczic/MicroWebSrv2.git) from the terminal:
    ```sh
    > git clone https://github.com/jczic/MicroWebSrv2.git
    ```

- **Solution 2**, download the [ZIP file](https://github.com/jczic/MicroWebSrv2/archive/master.zip) and extract it to a folder of your choice.

---

<a name="demo"></a>
# Demo

1. **Start the example:**
    ```sh
    > python3 main.py
    ```
    
2. **Open your web browser at:**
    - [http://localhost](http://localhost) to view the main page
    - [http://localhost/test-redir](http://localhost/test-redir) to test a redirection
    - [http://localhost/test-post](http://localhost/test-post) to test a POST form
    - [http://localhost/wstest.html](http://localhost/wstest.html) to test the WebSockets page
    - [http://localhost/wschat.html](http://localhost/wschat.html) to test the multi-users chat page
    - [http://localhost/test.pyhtml](http://localhost/test.pyhtml) to test a pyhtml template page

![WebSockets Chat](/img/wschat.png "WebSockets Chat")

---

<a name="usage"></a>
# Usage

```python
from MicroWebSrv2 import *
from time         import sleep

mws2 = MicroWebSrv2()
mws2.StartManaged()

# Main program loop until keyboard interrupt,
try :
    while True :
        sleep(1)
except KeyboardInterrupt :
    mws2.Stop()
```

---

<a name="documentation"></a>
# Documentation

  <a name="mws2-package"></a>
  - ## MicroWebSrv2 package

    The Python package comes with the following files:
      - **/MicroWebSrv2**
        - \_\_init\_\_.py
        - microWebSrv2.py
        - webRoute.py
        - httpRequest.py
        - httpResponse.py
        - **/libs**
          - XAsyncSockets.py
          - urlUtils.py
        - **/mods**
          - WebSockets.py
          - PyhtmlTemplate.py

    ---

  <a name="working-with-mws2"></a>
  - ## Working with microWebSrv2

    To work with **microWebSrv2**, you must first import the package as follows:
    ```python
    from MicroWebSrv2 import *
    ```

    There are 5 main elements with which you will work:
      - Web server (see [MicroWebSrv2 class](#mws2-class))
      - Routes (see [Web routes](#web-routes))
      - Requests (see [HttpRequest class](#request-class))
      - Responses (see [HttpResponse class](#response-class))
      - Modules (see [Additional modules](#modules))

    Now, you have everything you need to continue :')

    ---

    <a name="async-logic"></a>
    - ### Asynchronous logic

      **microWebSrv2** is based on a fully asynchronous I/Os logic.

      This means that many requests and responses can be processed concurrently,
      allowing other necessary processing at any time within a single thread.

      In addition, it is possible to use several shared workers in order to
      be able to parallelize processes that could be blocking.

      Finally, memory buffers required for data processing are pre-allocated
      as best as possible to maximize performance and prevent excessive memory requirements.

      Thus, it is possible to maintain several thousand persistent connections but also,
      to benefit from a low consumption of resources on embedded platforms.

      > **microWebSrv2** leans on the [XAsyncSockets](#xasyncsockets) layer.

      ---

    <a name="config-web-srv"></a>
    - ### Configuring web server

      Before starting **microWebSrv2** to listen to web requests, it is important to configure it correctly.

        - If you want to change the default server port or bind IP address, you must set the **BindAddress** property.
          ```python
          mws2.BindAddress = ('192.168.0.1', 12345)
          ```

        - If you want to define an another directory for web files, you must set the **RootPath** property.
          ```python
          mws2.RootPath = 'webfiles/root'
          ```

        - If you want a secure https web server, you must call the [**EnableSSL**](#mws2-enablessl) method.
          ```python
          mws2.EnableSSL(certFile='certificate.crt', keyFile='private-key.key')
          ```

        - If you want to redirect resources not found, you must set the **NotFoundURL** property.
          ```python
          mws2.NotFoundURL = '/'   # relative or absolute URL
          ```

        - If you want to set a pre-configured setting, you can call one of the following methods:
            - [SetEmbeddedConfig](#mws2-setembeddedconfig)
            - [SetLightConfig](#mws2-setlightconfig)
            - [SetNormalConfig](#mws2-setnormalconfig) (default setting)
            - [SetLargeConfig](#mws2-setlargeconfig)

        - If you want to set your custom settings, you can adjust the following properties:
            - [ConnQueueCapacity](#mws2-prop)
            - [BufferSlotsCount](#mws2-prop)
            - [BufferSlotSize](#mws2-prop)
            - [KeepAllocBufferSlots](#mws2-prop)
            - [MaxRequestContentLength](#mws2-prop)

        - If you want to change the default timeout to wait for requests data, you must set the **RequestsTimeoutSec** property.
          ```python
          mws2.RequestsTimeoutSec = 10
          ```

        - If you want to intercept logs to process them, you must set the [**OnLogging**](#mws2-onlogging) callback.
          ```python
          def OnMWS2Logging(microWebSrv2, msg, msgType) :
              print('Log from custom function: %s' % msg)

          mws2.OnLogging = OnMWS2Logging
          ```

      ---

      <a name="default-pages"></a>
      - ### Default pages

        Default pages are used as resources when requested paths point to directories.

        | Page filename |
        |---------------|
        | index.html    |
        | index.htm     |
        | default.html  |
        | default.htm   |

        > It is possible to add new default pages globally by calling [**MicroWebSrv2.AddDefaultPage**](#mws2-adddefaultpage) static method.

        ---

      <a name="mime-types"></a>
      - ### MIME types

        MIME types allow specific files as readable resources and that are transmitted with the corresponding content type.

        | Filename extension | MIME type |
        |--------------------|------------------------|
        | .txt               | text/plain             |
        | .htm               | text/html              |
        | .html              | text/html              |
        | .css               | text/css               |
        | .csv               | text/csv               |
        | .js                | application/javascript |
        | .xml               | application/xml        |
        | .xhtml             | application/xhtml+xml  |
        | .json              | application/json       |
        | .zip               | application/zip        |
        | .pdf               | application/pdf        |
        | .ts                | application/typescript |
        | .woff              | font/woff              |
        | .woff2             | font/woff2             |
        | .ttf               | font/ttf               |
        | .otf               | font/otf               |
        | .jpg               | image/jpeg             |
        | .jpeg              | image/jpeg             |
        | .png               | image/png              |
        | .gif               | image/gif              |
        | .svg               | image/svg+xml          |
        | .ico               | image/x-icon           |

        > It is possible to add new MIME types globally by calling [**MicroWebSrv2.AddMimeType**](#mws2-addmimetype) static method.

      ---

    <a name="start-web-srv"></a>
    - ### Starting web server

      To start **microWebSrv2** server, you must use one of the following methods:

        - **Start in a pool:**  
          The web server uses an existing asynchronous pool.  
          If you want to have more than one server, this is the right solution.  
          > For more documentation, see [**StartInPool(...)**](#mws2-startinpool) method.  
          > If you want details about pools, check the GitHub repository of [XAsyncSockets](https://github.com/jczic/XAsyncSockets) library.

        - **Start in a managed pool:**  
          The web server automatically creates a new managed asynchronous pool and uses it.  
          If you only need one server without more specific code, this is the right solution.  
          However, you will need to define some pool sizing parameters.  
          In this mode, a call to ```mws2.Stop()``` will release the pool.  
          > For more documentation, see [**StartManaged(...)**](#mws2-startmanaged) method.

      Example to start a dual http/https web server:
      ```python
      from MicroWebSrv2 import *
      from time         import sleep

      xasPool  = XAsyncSocketsPool()
      srvHttp  = MicroWebSrv2()
      srvHttps = MicroWebSrv2()

      srvHttps.EnableSSL( certFile = 'SSL-Cert/openhc2.crt',
                          keyFile  = 'SSL-Cert/openhc2.key' )

      srvHttp .StartInPool(xasPool)
      srvHttps.StartInPool(xasPool)
      
      xasPool.AsyncWaitEvents(threadsCount=1)

      try :
          while True :
              sleep(1)
      except KeyboardInterrupt :
          srvHttp .Stop()
          srvHttps.Stop()
          xasPool .StopWaitEvents()
      ```

      ---

    <a name="handling-routes"></a>
    - ### Handling web routes

      **microWebSrv2** have an easy and efficient web route system.  
      A simple handler function with a decorator allows you to process requests.

      Example of a processing handler:
      ```python
      @WebRoute(GET, '/test')
      def RequestTest(microWebSrv2, request) :
          request.Response.ReturnOkJSON({
              'ClientAddr' : request.UserAddress,
              'Accept'     : request.Accept,
              'UserAgent'  : request.UserAgent
          })
      ```
      > For more documentation, see [**Web Routes**](#web-routes) section.

      ---

    <a name="ssl-security"></a>
    - ### SSL/TLS security (HTTPS)

      **microWebSrv2** allow web server to apply the SSL/TLS security layer.  
      In this case, a certificate and its private key must be given (with an optional PEM file).

      If you want to test https mode, uncomment the ```mws2.EnableSSL(...)``` call in ```main.py``` file.  
      After restarting the demo program, open your browser at the following address:  
      [https://localhost](https://localhost)

      The **ssl library** must be implements ```SSLContext``` on Python version to support secured web server.

    ---

  <a name="xasyncsockets"></a>
  - ## About XAsyncSockets layer

    **XAsyncSockets** is an efficient Python/MicroPython library of managed asynchronous sockets.  
    > Available under MIT license on GitHub (same author):  
      [https://github.com/jczic/XAsyncSockets](https://github.com/jczic/XAsyncSockets)

    **XAsyncSockets** layer provides the following features:
      - Managed asynchronous sockets in a pool (up to thousands!)
      - Works directly with I/O to receive and send very quickly
      - Supports very large number of simultaneous TCP connections
      - Supports concurrent synchronous processing operations if necessary (threaded)
      - Implementation of TCP servers
      - Implementation of TCP clients
      - Implementation of UDP datagrams (sender and/or receiver)
      - TCP client can event after a specified size of data or a text line received
      - Each connections and receivings can waiting during a specified time
      - The reasons of TCP client closures are returned
      - Really robust, very fast and easy to use
      - Compatible with MicroPython implementation (sockets layer, FiFo queue, perf counter)

    ---

  <a name="mws2-class"></a>
  - ## MicroWebSrv2 Class

    **MicroWebSrv2** is the main class and is needed to create an instance of web server:
    ```python
    mws2 = MicroWebSrv2()
    ```

    ---

    <a name="mws2-static-func"></a>
    - ### MicroWebSrv2 static methods

      #### MicroWebSrv2.LoadModule(...)
      ```python
      @staticmethod
      def LoadModule(modName)
      # Loads a global and dedicated module for all instances of MicroWebSrv2.
      #   - Returns the instantiated class of the module.
      #     This instance can be used to configure global parameters and callbacks.
      #   - <modName> is the name of module and must be a not empty string.
      # An exception will be raised if an error occurs.
      ```

      #### MicroWebSrv2.HTMLEscape(...)
      ```python
      @staticmethod
      def HTMLEscape(s)
      # Escapes HTML special characters of a text to use it in HTML code.
      #   - Returns the escaped string of <s>.
      #   - <s> is a text that must be escaped and must be a string.
      # An exception can be raised if <s> is not correct.
      ```

      <a name="mws2-adddefaultpage"></a>
      #### MicroWebSrv2.AddDefaultPage(...)
      ```python
      @staticmethod
      def AddDefaultPage(filename)
      # Adds a new default page that it can be returned when a directory resource is requested.
      # Default pages are searched by order in list and file must be found in the directory.
      # Ex: AddDefaultPage('home.html')
      #   - No return value.
      #   - <filename> is the name of page file that will be searched and must be a not empty string.
      # An exception can be raised if <filename> is not correct.
      ```

      <a name="mws2-addmimetype"></a>
      #### MicroWebSrv2.AddMimeType(...)
      ```python
      @staticmethod
      def AddMimeType(ext, mimeType)
      # Adds a new MIME type to support specified file type and response content type.
      # Ex: AddMimeType('.tar', 'application/x-tar')
      #   - No return value.
      #   - <ext> is the file extention including the dot and must be a not empty string.
      #   - <mimeType> is the name of MIME type and must be a not empty string.
      # An exception can be raised if arguments are not correct.
      ```

      #### MicroWebSrv2.GetMimeTypeFromFilename(...)
      ```python
      @staticmethod
      def GetMimeTypeFromFilename(filename)
      # Obtains the name of MIME type corresponding to a filename.
      #   - Returns the name of MIME type found in string, returns None otherwise.
      #   - <filename> is a path to a file and must be a not empty string.
      ```

      ---

    <a name="mws2-func"></a>
    - ### MicroWebSrv2 instance methods

      <a name="mws2-startinpool"></a>
      #### mws2.StartInPool(...)
      ```python
      def StartInPool(self, asyncSocketsPool)
      # Starts the web server in an existing asynchronous pool.
      #   - No return value.
      #   - <asyncSocketsPool> is the asynchronous pool and must be an instantiated class of XAsyncSocketsPool.
      # An exception will be raised if an error occurs.
      ```

      <a name="mws2-startmanaged"></a>
      #### mws2.StartManaged(...)
      ```python
      def StartManaged(self, parllProcCount=1, procStackSize=0)
      # Starts the web server in a new and managed asynchronous pool.
      #   - No return value.
      #   - <parllProcCount> is the count of parallel processes and must be a positive integer or zero.
      #   - <procStackSize> is the stack size for each parallelized processes and must be a positive integer or zero.
      # If <parllProcCount> is 0, the calling thread is used and blocked to process all http connections.
      # If <parllProcCount> is 1, only one thread is reserved to process all http connections.
      # If <parllProcCount> is greater than 1, multiple threads are reserved to share and process all http connections.
      # If <procStackSize>  is 0, the default stack size is used on CPython and a value of 8192 is used on MicroPython.
      # A minimum value of 8*1024 is recommended for <procStackSize> but on CPython, the minimum value must be of 32*1024.
      # An exception will be raised if an error occurs.
      ```

      #### mws2.Stop(...)
      ```python
      def Stop(self)
      # Stops the web server.
      # If the server has started in managed mode, this automatically releases the asynchronous pool.
      #   - No return value.
      ```

      #### mws2.Log(...)
      ```python
      def Log(self, msg, msgType)
      # Logs the message of the specified type to the output or by calling the OnLogging callback.
      #   - No return value.
      #   - <msg> is the message to log and will be converted to string.
      #   - <msgType> can take following values:
      #      - MicroWebSrv2.DEBUG
      #      - MicroWebSrv2.INFO
      #      - MicroWebSrv2.WARNING
      #      - MicroWebSrv2.ERROR
      ```

      #### mws2.ResolvePhysicalPath(...)
      ```python
      def ResolvePhysicalPath(self, urlPath)
      # Resolves the specified relative URL path to the physical path.
      #   - Returns the physical path found or None.
      #   - <urlPath> is the relative URL path to resolve and must be a not empty string.
      # An exception can be raised if <urlPath> is not correct.
      ```

      <a name="mws2-enablessl"></a>
      #### mws2.EnableSSL(...)
      ```python
      def EnableSSL(self, certFile, keyFile, caFile=None)
      # Configures the web server to apply the SSL/TLS security layer (https).
      # Warning, the ssl library must be implements SSLContext on Python version to support secured web server.
      #   - No return value.
      #   - <certFile> is the path of the certificate file and must be a not empty string.
      #   - <keyFile> is the path of the private key file and must be a not empty string.
      #   - <caFile> is the path of a PEM file and must be a not empty string or None.
      # If the web server port in BindAddress is 80 (default http), it automatically switches to port 443 (default https).
      # An exception will be raised if an error occurs.
      ```

      #### mws2.DisableSSL(...)
      ```python
      def DisableSSL(self)
      # Configures the web server as SSL/TLS web server (https).
      #   - No return value.
      # If the web server port in BindAddress is 443 (default https), it automatically switches to port 80 (default http).
      # An exception can be raised if an error occurs.
      ```

      <a name="mws2-setembeddedconfig"></a>
      #### mws2.SetEmbeddedConfig(...)
      ```python
      def SetEmbeddedConfig(self)
      # Configures the web server with optimized parameters for an embedded deployment.
      #   - No return value.
      # Parameters set:
      #   - ConnQueueCapacity       = 8
      #   - BufferSlotsCount        = 16
      #   - BufferSlotSize          = 1024
      #   - KeepAllocBufferSlots    = True
      #   - MaxRequestContentLength = 16*1024
      # An exception can be raised if an error occurs.
      ```

      <a name="mws2-setlightconfig"></a>
      #### mws2.SetLightConfig(...)
      ```python
      def SetLightConfig(self)
      # Configures the web server with optimized parameters for a light deployment.
      #   - No return value.
      # Parameters set:
      #   - ConnQueueCapacity       = 64
      #   - BufferSlotsCount        = 128
      #   - BufferSlotSize          = 1024
      #   - KeepAllocBufferSlots    = True
      #   - MaxRequestContentLength = 512*1024
      # An exception can be raised if an error occurs.
      ```

      <a name="mws2-setnormalconfig"></a>
      #### mws2.SetNormalConfig(...)
      ```python
      def SetNormalConfig(self)
      # Configures the web server with optimized parameters for a normal deployment.
      # It is the default configuration when MicroWebSrv2 class is created.
      #   - No return value.
      # Parameters set:
      #   - ConnQueueCapacity       = 256
      #   - BufferSlotsCount        = 512
      #   - BufferSlotSize          = 4*1024
      #   - KeepAllocBufferSlots    = True
      #   - MaxRequestContentLength = 2*1024*1024
      # An exception can be raised if an error occurs.
      ```

      <a name="mws2-setlargeconfig"></a>
      #### mws2.SetLargeConfig(...)
      ```python
      def SetLargeConfig(self)
      # Configures the web server with optimized parameters for a large deployment.
      #   - No return value.
      # Parameters set:
      #   - ConnQueueCapacity       = 512
      #   - BufferSlotsCount        = 2*1024
      #   - BufferSlotSize          = 16*1024
      #   - KeepAllocBufferSlots    = True
      #   - MaxRequestContentLength = 8*1024*1024
      # An exception can be raised if an error occurs.
      ```

      ---

    <a name="mws2-prop"></a>
    - ### MicroWebSrv2 properties

      | Name                      |                 Type                |           Get           |           Set           | Description                                                                          |
      |---------------------------|:-----------------------------------:|:-----------------------:|:-----------------------:|--------------------------------------------------------------------------------------|
      | `IsRunning`               |                 bool                | Yes |            -            | *Indicates that the server is running.*                                              |
      | `ConnQueueCapacity`       |                 int                 | Yes | Yes | *Queue capacity of the TCP server (backlog).*                                        |
      | `BufferSlotsCount`        |                 int                 | Yes | Yes | *Number of pre-allocated memory buffer slots.*                                       |
      | `BufferSlotSize`          |                 int                 | Yes | Yes | *Size of each pre-allocated memory buffer slots.*                                    |
      | `KeepAllocBufferSlots`    |                 bool                | Yes | Yes | *Maintains the allocation of memory buffer slots.*                                   |
      | `MaxRequestContentLength` |                 int                 | Yes | Yes | *Maximum content length who can be processed by a request.*                          |
      | `BindAddress`             |                tuple                | Yes | Yes | *Local bind address of the TCP server such as a tuple of `(str_ip_addr, int_port)`.* |
      | `IsSSLEnabled`            |                 bool                | Yes |            -            | *Indicates that SSL/TLS security layer with certificate is currently enabled.*       |
      | `RootPath`                |                 str                 | Yes | Yes | *Path of the root folder that contains the web files.*                               |
      | `RequestsTimeoutSec`      |                 int                 | Yes | Yes | *Timeout in seconds to waiting the next data reception of requests.*                 |
      | `NotFoundURL`             |             str or None             | Yes | Yes | *URL used to redirects requests not found.*                                          |
      | `AllowAllOrigins`         |                 bool                | Yes | Yes | *Indicates that all resource origins of requests are allowed.*                       |
      | `CORSAllowAll`            |                 bool                | Yes | Yes | *Allows all CORS values for the pre-flight requests (OPTIONS).*                      |
      | `OnLogging`               | [callback](#mws2-onlogging) or None | Yes | Yes | *Callback function when the server logs information.*                                |

      > **Definition of the above callback functions:**

      <a name="mws2-onlogging"></a>
      ```python
      def OnLogging(microWebSrv2, msg, msgType)
      # <microWebSrv2> is of type MicroWebSrv2
      # <msg> is of type str
      # <msgType> can take following values:
      #    - MicroWebSrv2.DEBUG
      #    - MicroWebSrv2.INFO
      #    - MicroWebSrv2.WARNING
      #    - MicroWebSrv2.ERROR
      ```

    ---

  <a name="web-routes"></a>
  - ## Web Routes

    Web routes allow you to define conditional access paths to
    specific resources and react to corresponding http requests.  
    They also provide the possibility of using freer
    conditions that can be retrieved as input elements.

    In **microWebSrv2**, a web route is composed by a **processing handler**,
    a **requested method**, a **requested path** and an optional **name**.  
    The requested path can also consist of variable parts that
    can be retrieved as arguments.

    Finally, during an http request, if the method and path match to a route,
    the processing handler is called with the expected arguments.

    ---

    <a name="route-process"></a>
    - ### Route Processing

      A route processing is an handler function decorated by the setting of the route.  
      This setting uses the ```@WebRoute``` decorator whose definition is as follows:
      ```python
      @WebRoute(method, routePath, name=None)
      # <method> is the http requested method and must be a not empty string.
      # <routePath> is the http requested path and must be a not empty string.
      # <name> is an optional route name and must be a string or None.
      ```

      The handler function definition is as follows:
      ```python
      @WebRoute(...)
      def RequestHandler(microWebSrv2, request)
      # <microWebSrv2> is of type MicroWebSrv2
      # <request> is of type HttpRequest
      ```

      The **method argument** can be a string but also one of the following constants:  
      ```GET```, ```HEAD```, ```POST```, ```PUT```, ```DELETE```, ```OPTIONS```, ```PATCH```

      The **routePath argument** must always starts by ```/``` and specifies the relative URL of the route.

      > Note that a route processing handler is **global** and can be called by any instance of MicroWebSrv2 class.

      Example of processing handlers:
      ```python
      @WebRoute(GET, '/my-resource')
      def RequestHandler1(microWebSrv2, request) :
          pass
      ```
      ```python
      @WebRoute(POST, '/test/virtual-page.html', 'myTestRoute')
      def RequestHandler2(microWebSrv2, request) :
          pass
      ```
      ```python
      @WebRoute(OPTIONS, '/')
      def RequestHandler3(microWebSrv2, request) :
          pass
      ```

      ---

    <a name="route-args"></a>
    - ### Route Arguments

      It is possible to include route arguments that can be retrieved as input elements.  
      These arguments are directly defined in the **requested path**
      by naming and framing them with ```<```and ```>``` as follows:
      ```python
      @WebRoute(GET, '/users/<id>/profile/<property>')
      ```
      In this web route, two arguments are defined: ```id``` and ```property```.  
      Thus, the route is variable and corresponds to the **requested path** from which any argument can be used.
      ```python
      '/users/123/profile/firstname'
      ```

      So, the handler function definition is extended as follows:
      ```python
      @WebRoute(...)
      def RequestHandler(microWebSrv2, request, args)
      # <microWebSrv2> is of type MicroWebSrv2
      # <request> is of type HttpRequest
      # <args> is a dictionary of route arguments
      ```
      Now, ```args``` can be used like ```args['id']``` or ```args['property']```.  
      Note that values can be strings but also integers directly.

      ---

    <a name="route-func"></a>
    - ### Route Methods

      #### RegisterRoute(...)
      ```python
      def RegisterRoute(handler, method, routePath, name=None)
      # Registers a global web route directly, without decorator usage.
      #   - No return value.
      #   - <handler> is the route processing handler and must be a function (see above).
      #   - <method> is the http requested method and must be a not empty string.
      #   - <routePath> is the http requested path and must be a not empty string.
      #   - <name> is an optional route name and must be a string or None.
      # An exception can be raised if arguments are not correct.
      ```

      #### ResolveRoute(...)
      ```python
      def ResolveRoute(method, path)
      # Resolves a web route using a method and a path.
      #   - Returns a RouteResult class if no error occurred and route was found, returns None otherwise.
      #   - <method> is an http method and must be of string type.
      #   - <path> is an http relative path and must be of string type.
      ```
      The **RouteResult** class exposes the following properties:

      | Name        |        Type        |
      |-------------|:------------------:|
      | `Handler`   | processing handler |
      | `Method`    |       string       |
      | `RoutePath` |       string       |
      | `Name`      |   string or None   |
      | `Args`      |     dictionary     |

      #### PathFromRoute(...)
      ```python
      def PathFromRoute(routeName, routeArgs={ })
      # Constructs the relative path from the route name and route arguments.
      #   - Returns a string that is the relative path.
      #   - <routeName> is the name of the web route and must be a not empty string.
      #   - <routeArgs> is a dictionary of needed argument names and values.
      # An exception can be raised if arguments are not correct or route was not found.
      ```

    ---

  <a name="request-class"></a>
  - ## HttpRequest Class

    HttpRequest class represents a received http request by the web server.  
    It can be obtained in web route handlers or in modules.  
    It also allows you to process the response.

    ---

    <a name="request-func"></a>
    - ### HttpRequest instance methods

      #### httpRequest.GetPostedURLEncodedForm(...)
      ```python
      def GetPostedURLEncodedForm(self)
      # Obtains name/value pairs from an URL encoded form.
      # The http request must have an URL encoded form content.
      #   - Returns a dictionary of name/value pairs (string for both).
      ```

      #### httpRequest.GetPostedJSONObject(...)
      ```python
      def GetPostedJSONObject(self)
      # Obtains the object posted in JSON format.
      # The http request must have a JSON content.
      #   - Returns any type of object or None.
      ```

      #### httpRequest.GetHeader(...)
      ```python
      def GetHeader(self, name)
      # Obtains the value of an http request header.
      #   - Returns always a string value.
      #   - <name> must be a not empty string.
      # An exception can be raised if <name> is not correct.
      ```

      #### httpRequest.CheckBasicAuth(...)
      ```python
      def CheckBasicAuth(self, username, password)
      # Checks if the http request is authenticated with the "Basic" method.
      #   - Returns True if the authentication is correct, returns False otherwise.
      #   - <username> must be a string.
      #   - <password> must be a string.
      # An exception can be raised if arguments are not correct.
      ```

      #### httpRequest.CheckBearerAuth(...)
      ```python
      def CheckBearerAuth(self, token)
      # Checks if the http request is authenticated with the "Bearer" method.
      #   - Returns True if authentication is correct, returns False otherwise.
      #   - <token> is the session token and must be a string.
      # An exception can be raised if <token> is not correct.
      ```

      ---

    <a name="request-prop"></a>
    - ### HttpRequest properties

      | Name              |               Type              |           Get           | Set | Description                                                                                 |
      |-------------------|:-------------------------------:|:-----------------------:|:---:|---------------------------------------------------------------------------------------------|
      | `UserAddress`     |              tuple              | Yes |  -  | *User remote address of the http connection such as a tuple of `(str_ip_addr, int_port)`.*  |
      | `IsSSL`           |               bool              | Yes |  -  | *Indicates that the http connection is secured by SSL/TLS security layer with certificate.* |
      | `HttpVer`         |               str               | Yes |  -  | *Version of the client protocol of the http connection.*                                    |
      | `Method`          |               str               | Yes |  -  | *Name of the method transmitted with this request.*                                         |
      | `Path`            |               str               | Yes |  -  | *Path of the resource transmitted with this request.*                                       |
      | `QueryString`     |               str               | Yes |  -  | *Full query string transmitted with this request.*                                          |
      | `QueryParams`     |               dict              | Yes |  -  | *Parameters of the query string transmitted with this request.*                             |
      | `Host`            |               str               | Yes |  -  | *Hostname transmitted with this request.*                                                   |
      | `Accept`          |               list              | Yes |  -  | *List of possible content types expected in response to this request.*                      |
      | `AcceptEncodings` |               list              | Yes |  -  | *List of possible encodings expected in response to this request.*                          |
      | `AcceptLanguages` |               list              | Yes |  -  | *List of possible languages expected in response to this request.                           |
      | `Cookies`         |               list              | Yes |  -  | *List of cookies transmitted with this request.*                                            |
      | `CacheControl`    |               str               | Yes |  -  | *Control of cache transmitted with this request.*                                           |
      | `Referer`         |               str               | Yes |  -  | *Referer address transmitted with this request.*                                            |
      | `ContentType`     |               str               | Yes |  -  | *Type of the content included in this request.*                                             |
      | `ContentLength`   |               int               | Yes |  -  | *Length of the content included in this request.*                                           |
      | `UserAgent`       |               str               | Yes |  -  | *Name of the client agent transmitted with this request.*                                   |
      | `Authorization`   |               str               | Yes |  -  | *Authorization string transmitted with this request.*                                       |
      | `Origin`          |               str               | Yes |  -  | *Address of the origin transmitted with this request.*                                      |
      | `IsKeepAlive`     |               bool              | Yes |  -  | *Indicates that the http connection can be keep alive.*                                     |
      | `IsUpgrade`       |               bool              | Yes |  -  | *Indicates that the http connection must be upgraded.*                                      |
      | `Upgrade`         |               str               | Yes |  -  | *Upgrade string transmitted with this request.*                                             |
      | `Content`         |        memoryview or None       | Yes |  -  | *Raw data of the content included in this request.*                                         |
      | `Response`        | [HttpResponse](#response-class) | Yes |  -  | *Http response related to this connection.*                                                 |
      | `XAsyncTCPClient` |         XAsyncTCPClient         | Yes |  -  | *Asynchronous TCP connection from the XAsyncSockets library.*                               |

    ---

  <a name="response-class"></a>
  - ## HttpResponse Class

    HttpResponse class is used to manage the reponse of an http request.  
    It can be obtained by the ```Response``` property of an instantiated HttpRequest.   

    ---

    <a name="response-func"></a>
    - ### HttpResponse instance methods

      #### httpResponse.SetHeader(...)
      ```python
      def SetHeader(self, name, value)
      # Set a header to the http response.
      #   - No return value.
      #   - <name> must be a not empty string.
      #   - <value> may be anything but cannot be None.
      # An exception can be raised if arguments are not correct.
      ```

      #### httpResponse.SwitchingProtocols(...)
      ```python
      def SwitchingProtocols(self, upgrade)
      # Sends a special http response to upgrade the connection.
      #   - No return value.
      #   - <upgrade> must be a not empty string.
      # An exception can be raised if <upgrade> is not correct.
      ```

      #### httpResponse.ReturnStream(...)
      ```python
      def ReturnStream(self, code, stream)
      # Sends a stream content to the http response.
      #   - No return value.
      #   - <code> is the http status code and must be a positive integer.
      #   - <stream> must be a readable buffer protocol object.
      # An exception can be raised if arguments are not correct.
      ```

      #### httpResponse.Return(...)
      ```python
      def Return(self, code, content=None)
      # Sends an http response with or without content.
      #   - No return value.
      #   - <code> is the http status code and must be a positive integer.
      #   - <content> must be a string or in bytes or convertible into bytes or None.
      # An exception can be raised if arguments are not correct.
      ```

      #### httpResponse.ReturnJSON(...)
      ```python
      def ReturnJSON(self, code, obj)
      # Sends an http response with a JSON content.
      #   - No return value.
      #   - <code> is the http status code and must be a positive integer.
      #   - <obj> can be anything and will be serialized (stringify process).
      # An exception can be raised if arguments are not correct.
      ```

      #### httpResponse.ReturnOk(...)
      ```python
      def ReturnOk(self, content=None)
      # Sends a success http response with or without content.
      #   - No return value.
      #   - <content> must be a string or in bytes or convertible into bytes or None.
      # An exception can be raised if <content> is not correct.
      ```

      #### httpResponse.ReturnOkJSON(...)
      ```python
      def ReturnOkJSON(self, obj)
      # Sends a success http response with a JSON content.
      #   - No return value.
      #   - <obj> can be anything and will be serialized (stringify process).
      # An exception can be raised if <obj> is not correct.
      ```

      #### httpResponse.ReturnFile(...)
      ```python
      def ReturnFile(self, filename, attachmentName=None)
      # Sends a file to the http response.
      #   - No return value.
      #   - <filename> is the physical path of the file and must be a not empty string.
      #   - <attachmentName> can be the name of the file to save, in string, or None.
      #     If None, the user will see it "on the fly" in his browser, he will can save it otherwise.
      # An exception can be raised if arguments are not correct.
      ```

      #### httpResponse.ReturnNotModified(...)
      ```python
      def ReturnNotModified(self)
      # Sends a not modified http response.
      # Used in resources caching context.
      #   - No return value.
      ```

      #### httpResponse.ReturnRedirect(...)
      ```python
      def ReturnRedirect(self, location)
      # Sends a temporary redirect http response.
      # Used to move the user to a new url.
      #   - No return value.
      #   - <location> is the relative or absolute URL and must be a not empty string.
      # An exception can be raised if <location> is not correct.
      ```

      #### httpResponse.ReturnBadRequest(...)
      ```python
      def ReturnBadRequest(self)
      # Sends a bad request http response.
      # Used for user request error.
      #   - No return value.

      ```

      #### httpResponse.ReturnUnauthorized(...)
      ```python
      def ReturnUnauthorized(self, typeName, realm=None)
      # Sends an unauthorized http response.
      # Used if the user needs to authenticate.
      #   - No return value.
      #   - <typeName> is the name of required authentication and must be a not empty string.
      #   - <realm> is a name for the protected resource and can be a string or None.
      # An exception can be raised if arguments are not correct.
      ```

      #### httpResponse.ReturnForbidden(...)
      ```python
      def ReturnForbidden(self)
      # Sends a forbidden http response.
      # Used to indicate a denied access.
      #   - No return value.

      ```

      #### httpResponse.ReturnNotFound(...)
      ```python
      def ReturnNotFound(self)
      # Sends a not found http response.
      # Used to indicate that the resource does not exist.
      #   - No return value.

      ```

      #### httpResponse.ReturnMethodNotAllowed(...)
      ```python
      def ReturnMethodNotAllowed(self)
      # Sends a method not allowed http response.
      # Used if the method is not supported for resource.
      #   - No return value.

      ```

      #### httpResponse.ReturnEntityTooLarge(...)
      ```python
      def ReturnEntityTooLarge(self)
      # Sends an entity too large http response.
      # Used for an excessive content size.
      #   - No return value.

      ```

      #### httpResponse.ReturnInternalServerError(...)
      ```python
      def ReturnInternalServerError(self)
      # Sends an internal server error http response.
      # Used if an error has occurred.
      #   - No return value.

      ```

      #### httpResponse.ReturnNotImplemented(...)
      ```python
      def ReturnNotImplemented(self)
      # Sends a not implemented http response.
      # Used in case of a non-existent process of the resource.
      #   - No return value.

      ```

      #### httpResponse.ReturnServiceUnavailable(...)
      ```python
      def ReturnServiceUnavailable(self)
      # Sends a service unavailable http response.
      # Used if it is currently impossible to process the request.
      #   - No return value.

      ```

      #### httpResponse.ReturnBasicAuthRequired(...)
      ```python
      def ReturnBasicAuthRequired(self)
      # Sends an http response to indicate that "Basic" authentication is required.
      #   - No return value.

      ```

      #### httpResponse.ReturnBearerAuthRequired(...)
      ```python
      def ReturnBearerAuthRequired(self)
      # Sends an http response to indicate that "Bearer" authentication is required.
      #   - No return value.

      ```

      ---

    <a name="response-prop"></a>
    - ### HttpResponse properties

      | Name                       |              Type                    |           Get           |           Set           | Description                                                                                 |
      |----------------------------|:------------------------------------:|:-----------------------:|:-----------------------:|---------------------------------------------------------------------------------------------|
      | `Request`                  |    [HttpRequest](#request-class)     | Yes |            -            | *Http request related to this response.*                                                    |
      | `UserAddress`              |               tuple                  | Yes |            -            | *User remote address of the http connection such as a tuple of `(str_ip_addr, int_port)`.*  |
      | `IsSSL`                    |                bool                  | Yes |            -            | *Indicates that the http connection is secured by SSL/TLS security layer with certificate.* |
      | `AllowCaching`             |                bool                  | Yes | Yes | *Indicates to the user the possible caching of this response.*                              |
      | `AccessControlAllowOrigin` |            str or None               | Yes | Yes | *Indicates to the user the allowed resource origin.*                                        |
      | `ContentType`              |            str or None               | Yes | Yes | *Type of the content of this response.*                                                     |
      | `ContentCharset`           |            str or None               | Yes | Yes | *Encoding charset used for the content of this response.*                                   |
      | `ContentLength`            |                int                   | Yes | Yes | *Length of the content of this response.*                                                   |
      | `HeadersSent`              |                bool                  | Yes |            -            | *Indicates that response http headers was already sent.*                                    |
      | `OnSent`                   | [callback](#response-onsent) or None | Yes | Yes | *Callback function when response is fully sent.*                                            |

      > **Definition of the above callback functions:**

      <a name="response-onsent"></a>
      ```python
      def OnSent(microWebSrv2, response)
      # <microWebSrv2> is of type MicroWebSrv2
      # <response> is of type HttpResponse
      ```

    ---

  <a name="modules"></a>
  - ## Additional modules

    **microWebSrv2** supports additional modules that can be called during the
    processing of a web request and can then decide whether or not to intercept it.  
    Modules can simply analyze http requests or responding to them so that
    they cannot continue their normal pipe-line processing.

    A module file must be placed in the "```/mods```" directory of the package
    and must define a class of the same name.  
    In addition, this class must implement the ```OnRequest(...)``` method
    that will be called at each http request.

    Example of a module named "```TestMod.py```":
    ```python
    class TestMod :

        def OnRequest(self, microWebSrv2, request) :
            print('TestMod: Request received from %s:%s' % request.UserAddress)
    ```

    ---

    <a name="websockets-mod"></a>
    - ## WebSockets Module

      **WebSockets module** must be loaded first by **microWebSrv2** to process WebSocket connections.  
      These are fully managed asynchronous I/Os and really many connections can be processed.  
      After module loaded, do not forget to assign the callback [OnWebSocketAccepted](#ws-mod-onwebsocketaccepted).  
      If you need to select and process a sub-protocol, you must assign the callback [OnWebSocketProtocol](#ws-mod-onwebsocketprotocol).  
      ```python
      from MicroWebSrv2 import *

      WS_CHAT_SUB_PROTOCOL = 'myGreatChat-v1'

      def OnWebSocketProtocol(microWebSrv2, protocols) :
          if WS_CHAT_SUB_PROTOCOL in protocols :
              return WS_CHAT_SUB_PROTOCOL

      def OnWebSocketAccepted(microWebSrv2, webSocket) :
          print('New WebSocket (myGreatChat proto) accepted from %s:%s.' % webSocket.Request.UserAddress)

      wsMod = MicroWebSrv2.LoadModule('WebSockets')
      wsMod.OnWebSocketProtocol = OnWebSocketProtocol
      wsMod.OnWebSocketAccepted = OnWebSocketAccepted
      ```

      ---
    
      <a name="websockets-mod-prop"></a>
      - ### WebSockets module properties

        | Name                  |                   Type                          |           Get           |           Set           | Description                                                                    |
        |-----------------------|:-----------------------------------------------:|:-----------------------:|:-----------------------:|--------------------------------------------------------------------------------|
        | `OnWebSocketProtocol` | [callback](#ws-mod-onwebsocketprotocol) or None | Yes | Yes | *Callback function when a new WebSocket connection negociates a sub-protocol.* |
        | `OnWebSocketAccepted` | [callback](#ws-mod-onwebsocketaccepted) or None | Yes | Yes | *Callback function when a new WebSocket connection is accepted.*               |

        > **Definition of the above callback functions:**

        <a name="ws-mod-onwebsocketprotocol"></a>
        ```python
        def OnWebSocketProtocol(microWebSrv2, protocols)
        # <microWebSrv2> is of type MicroWebSrv2
        # <protocols> is a string list of proposed protocols
        # RETURN: If you select a protocol, you must return it (the same as in the list)
        ```

        <a name="ws-mod-onwebsocketaccepted"></a>
        ```python
        def OnWebSocketAccepted(microWebSrv2, webSocket)
        # <microWebSrv2> is of type MicroWebSrv2
        # <webSocket> is of type WebSocket
        ```

        ---

      <a name="websocket-class"></a>
      - ### WebSocket Class

        WebSocket class is automatically instantiated by WebSockets module.  
        A WebSocket can be obtained when a new connection is accepted in the callback [OnWebSocketAccepted](#ws-mod-onwebsocketaccepted).  
        It is also important to assign WebSocket callbacks in order to receive the various events.  

        ---

        <a name="websocket-func"></a>
        - ### WebSocket instance methods

          #### webSocket.SendTextMessage(...)
          ```python
          def SendTextMessage(self, msg)
          # Sends a text message through the WebSocket.
          #   - Returns True or False.
          #   - <msg> must be a not empty string.
          # An exception can be raised if <msg> is not correct.
          ```

          #### webSocket.SendBinaryMessage(...)
          ```python
          def SendBinaryMessage(self, msg)
          # Sends a binary message through the WebSocket.
          #   - Returns True or False.
          #   - <msg> must be in bytes or convertible into bytes and not empty.
          # An exception can be raised if <msg> is not correct.
          ```

          #### webSocket.Close(...)
          ```python
          def Close(self)
          # Closes the WebSocket.
          #   - No return value.
          ```

          ---

        <a name="websocket-prop"></a>
        - ### WebSocket properties

          | Name                   |                   Type                  |           Get           |           Set           | Description                                     |
          |------------------------|:---------------------------------------:|:-----------------------:|:-----------------------:|-------------------------------------------------|
          | `Request`              |     [ HttpRequest](#request-class)      | Yes |            -            | *Http request related to this connection.*      |
          | `IsClosed`             |                   bool                  | Yes |            -            | *Indicates that connection is closed.*          |
          | `WaitFrameTimeoutSec`  |                   int                   | Yes | Yes | *Timeout in seconds to waiting next frame.*     |
          | `MaxRecvMessageLength` |               int or None               | Yes | Yes | *Maximum length of messages to receive.*        |
          | `OnTextMessage`        |  [callback](#ws-ontextmessage) or None  | Yes | Yes | *Callback function to receive text messages.*   |
          | `OnBinaryMessage`      | [callback](#ws-onbinarymessage) or None | Yes | Yes | *Callback function to receive binary messages.* |
          | `OnClosed`             |     [callback](#ws-onclosed) or None    | Yes | Yes | *Callback function when connection is closed.*  |

          > **Definition of the above callback functions:**

          <a name="ws-ontextmessage"></a>
          ```python
          def OnTextMessage(webSocket, msg)
          # <webSocket> is of type WebSocket
          # <msg> is of type str
          ```

          <a name="ws-onbinarymessage"></a>
          ```python
          def OnBinaryMessage(webSocket, msg)
          # <webSocket> is of type WebSocket
          # <msg> is of type memoryview
          ```

          <a name="ws-onclosed"></a>
          ```python
          def OnClosed(webSocket)
          # <webSocket> is of type WebSocket
          ```

    ---

    <a name="pyhtmltemplate-mod"></a>
    - ## PyhtmlTemplate Module

      **PyhtmlTemplate module** must be loaded first by **microWebSrv2** to process **.pyhtml** pages.  
      With it, you will be able to render HTML pages directly integrating Python/MicroPython language.  
      ```python
      from MicroWebSrv2 import *

      pyhtmlTemplateMod = MicroWebSrv2.LoadModule('PyhtmlTemplate')
      pyhtmlTemplateMod.ShowDebug = True
      ```

      In the pages **.pyhtml**, you must use special instructions:  
      Please, consult the **[documentation](https://github.com/jczic/MicroWebSrv2#pyhtmltemplate-mod)** on the GitHub project page.

      See the **[test.pyhtml](https://github.com/jczic/MicroWebSrv2/blob/master/www/test.pyhtml)** page for an example.

      ---

      <a name="pyhtmltemplate-func"></a>
      - ### PyhtmlTemplate module instance methods

        #### pyhtmlTemplateMod.SetGlobalVar(...)
        ```python
        def SetGlobalVar(self, globalVarName, globalVar)
        # Defines a global variable accessible by all pyhtml pages.
        #   - No return value.
        #   - <globalVarName> must be a not empty string.
        #   - <globalVar> must be an object or None.
        # An exception can be raised if <globalVarName> is not correct.
        ```

        #### pyhtmlTemplateMod.GetGlobalVar(...)
        ```python
        def GetGlobalVar(self, globalVarName)
        # Retrieves a global variable accessible by all pyhtml pages.
        #   - Returns an object or None.
        #   - <globalVarName> must be a not empty string.
        # An exception can be raised if <globalVarName> is not correct.
        ```

        ---

      <a name="pyhtmltemplate-prop"></a>
      - ### PyhtmlTemplate module properties

        | Name        |  Type  |           Get           |           Set           | Description                       |
        |-------------|:------:|:-----------------------:|:-----------------------:|-----------------------------------|
        | `ShowDebug` |  bool  | Yes | Yes | *Enables debugging on web pages.* |

---

<a name="author"></a>
## Author

  **Jean-Christophe Bos** (France, Paris)
  - GitHub: *[@jczic](https://github.com/jczic)*
  - Email:  *<jcb@hc2.fr>*
  - Web:    *[www.hc2.fr](https://www.hc2.fr)*

---

<a name="license"></a>
## License

  - Copyright (c) 2019 [Jean-Christophe Bos](https://www.linkedin.com/in/jczic) & [HC²](https://www.hc2.fr).
  - This project is [MIT](https://github.com/jczic/MicroWebSrv2/blob/master/LICENSE.md) licensed.

---

<br />
