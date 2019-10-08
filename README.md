# microWebSrv2

![Release](https://img.shields.io/github/v/release/jczic/microwebsrv2?include_prereleases&color=success)
![Size](https://img.shields.io/github/languages/code-size/jczic/microwebsrv2?color=blue)
![MicroPython](https://img.shields.io/badge/micropython-Ok-green.svg)
![Python](https://img.shields.io/badge/python-Ok-green.svg)
![License](https://img.shields.io/github/license/jczic/microwebsrv2?color=yellow)

> Description

![HC²](hc2.png "HC²")

---

## :bookmark_tabs: Table of Contents

- [**About**](#about)
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
    - [SSL/TLS security](#ssl-security)
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
    - [Static Methods](#request-static-func)
    - [Instance Methods](#request-func)
    - [Properties](#request-prop)
  - [**HttpResponse Class**](#response-class)
    - [Static Methods](#response-static-func)
    - [Instance Methods](#response-func)
    - [Properties](#response-prop)
  - [**Additional modules**](#modules)
    - [**WebSockets Module**](#websockets-mod)
      - [**WebSocket Class**](#websocket-class)
        - [Static Methods](#websocket-static-func)
        - [Instance Methods](#websocket-func)
        - [Properties](#websocket-prop)
- [**Author**](#author)
- [**License**](#license)

---

<a name="about"></a>
## :question: About

---

<a name="install"></a>
## :radio_button: Install

```python
def toto(coucou=titi) :
    pass
    x = 5
    y = 'bonjour'
```

---

<a name="demo"></a>
## :rocket: Demo

1. Start the example :
    ```sh
    > python3 main.py
    ```
    
2. Open your web browser at :
    - [https://localhost](https://localhost) to view the main page
    - [https://localhost/test-redir](https://localhost/test-redir) to test a redirection
    - [https://localhost/test-post](https://localhost/test-post) to test a POST form
    - [https://localhost/wstest.html](https://localhost/wstest.html) to test the WebSockets page
    - [https://localhost/wschat.html](https://localhost/wschat.html) to test the multi-users chat page

---

<a name="usage"></a>
## :gear: Usage

---
```python
def Toto(titi=123)
```
  - `titi` : Ceci est un test.
  | Parameter | Description |
  | - | - |
  | `titi` | Ceci est un test. |
  - `titi` : Ceci est un test.
  - `tototruc` : Ceci est un test.

---

<a name="documentation"></a>
## :books: Documentation

  <a name="mws2-package"></a>
  - ## MicroWebSrv2 package

  <a name="working-with-mws2"></a>
  - ## Working with microWebSrv2

    <a name="async-logic"></a>
    - ### Asynchronous logic

    <a name="config-web-srv"></a>
    - ### Configuring web server

      <a name="default-pages"></a>
      - ### Default pages

        | Page filename |
        |---------------|
        | index.html    |
        | index.htm     |
        | default.htm   |
        | default.htm   |

      <a name="mime-types"></a>
      - ### MIME types

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

    <a name="start-web-srv"></a>
    - ### Starting web server

    <a name="handling-routes"></a>
    - ### Handling web routes

    <a name="ssl-security"></a>
    - ### SSL/TLS security

  <a name="xasyncsockets"></a>
  - ## About XAsyncSockets layer

  <a name="mws2-class"></a>
  - ## MicroWebSrv2 Class

    <a name="mws2-static-func"></a>
    - ### Static Methods

    <a name="mws2-func"></a>
    - ### Instance Methods

    <a name="mws2-prop"></a>
    - ### Properties

      | Name                      |                 Type                |           Get           |           Set           | Description                                                                          |
      |---------------------------|:-----------------------------------:|:-----------------------:|:-----------------------:|--------------------------------------------------------------------------------------|
      | `IsRunning`               |                 bool                | :ballot_box_with_check: |            -            | *Indicates that the server is running.*                                              |
      | `ConnQueueCapacity`       |                 int                 | :ballot_box_with_check: | :ballot_box_with_check: | *Queue capacity of the TCP server (backlog).*                                        |
      | `BufferSlotsCount`        |                 int                 | :ballot_box_with_check: | :ballot_box_with_check: | *Number of pre-allocated memory buffer slots.*                                       |
      | `BufferSlotSize`          |                 int                 | :ballot_box_with_check: | :ballot_box_with_check: | *Size of each pre-allocated memory buffer slots.*                                    |
      | `KeepAllocBufferSlots`    |                 bool                | :ballot_box_with_check: | :ballot_box_with_check: | *Maintains the allocation of memory buffer slots.*                                   |
      | `MaxRequestContentLength` |                 int                 | :ballot_box_with_check: | :ballot_box_with_check: | *Maximum content length who can be processed by a request.*                          |
      | `BindAddress`             |                tuple                | :ballot_box_with_check: | :ballot_box_with_check: | *Local bind address of the TCP server such as a tuple of `(str_ip_addr, int_port)`.* |
      | `IsSSLEnabled`            |                 bool                | :ballot_box_with_check: |            -            | *Indicates that SSL/TLS security layer with certificate is currently enabled.*       |
      | `RootPath`                |                 str                 | :ballot_box_with_check: | :ballot_box_with_check: | *Path of the root folder that contains the web files.*                               |
      | `RequestsTimeoutSec`      |                 int                 | :ballot_box_with_check: | :ballot_box_with_check: | *Timeout in seconds to waiting the next data reception of requests.*                 |
      | `NotFoundURL`             |             str or None             | :ballot_box_with_check: | :ballot_box_with_check: | *URL used to redirects requests not found.*                                          |
      | `OnLogging`               | [callback](#mws2-onlogging) or None | :ballot_box_with_check: | :ballot_box_with_check: | *Callback function when the server logs information.*                                |

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

<a name="web-routes"></a>
  - ## Web Routes

    <a name="route-process"></a>
    - ### Route Processing

    <a name="route-args"></a>
    - ### Route Arguments

    <a name="route-func"></a>
    - ### Route Methods

  <a name="request-class"></a>
  - ## HttpRequest Class

    <a name="request-static-func"></a>
    - ### Static Methods

    <a name="request-func"></a>
    - ### Instance Methods

    <a name="request-prop"></a>
    - ### Properties

      | Name              |               Type              |           Get           | Set | Description                                                                                 |
      |-------------------|:-------------------------------:|:-----------------------:|:---:|---------------------------------------------------------------------------------------------|
      | `UserAddress`     |              tuple              | :ballot_box_with_check: |  -  | *User remote address of the http connection such as a tuple of `(str_ip_addr, int_port)`.*  |
      | `IsSSL`           |               bool              | :ballot_box_with_check: |  -  | *Indicates that the http connection is secured by SSL/TLS security layer with certificate.* |
      | `HttpVer`         |               str               | :ballot_box_with_check: |  -  | *Version of the client protocol of the http connection.*                                    |
      | `Method`          |               str               | :ballot_box_with_check: |  -  | *Name of the method transmitted with this request.*                                         |
      | `Path`            |               str               | :ballot_box_with_check: |  -  | *Path of the ressource transmitted with this request.*                                      |
      | `QueryString`     |               str               | :ballot_box_with_check: |  -  | *Full query string transmitted with this request.*                                          |
      | `QueryParams`     |               dict              | :ballot_box_with_check: |  -  | *Parameters of the query string transmitted with this request.*                             |
      | `Host`            |               str               | :ballot_box_with_check: |  -  | *Hostname transmitted with this request.*                                                   |
      | `Accept`          |               list              | :ballot_box_with_check: |  -  | *List of possible content types expected in response to this request.*                      |
      | `AcceptEncodings` |               list              | :ballot_box_with_check: |  -  | *List of possible encodings expected in response to this request.*                          |
      | `AcceptLanguages` |               list              | :ballot_box_with_check: |  -  | *List of possible languages expected in response to this request.                           |
      | `Cookies`         |               list              | :ballot_box_with_check: |  -  | *List of cookies transmitted with this request.*                                            |
      | `CacheControl`    |               str               | :ballot_box_with_check: |  -  | *Control of cache transmitted with this request.*                                           |
      | `Referer`         |               str               | :ballot_box_with_check: |  -  | *Referer address transmitted with this request.*                                            |
      | `ContentType`     |               str               | :ballot_box_with_check: |  -  | *Type of the content included in this request.*                                             |
      | `ContentLength`   |               int               | :ballot_box_with_check: |  -  | *Length of the content included in this request.*                                           |
      | `UserAgent`       |               str               | :ballot_box_with_check: |  -  | *Name of the client agent transmitted with this request.*                                   |
      | `Authorization`   |               str               | :ballot_box_with_check: |  -  | *Authorization string transmitted with this request.*                                       |
      | `Origin`          |               str               | :ballot_box_with_check: |  -  | *Address of the origin transmitted with this request.*                                      |
      | `IsKeepAlive`     |               bool              | :ballot_box_with_check: |  -  | *Indicates that the http connection can be keep alive.*                                     |
      | `IsUpgrade`       |               bool              | :ballot_box_with_check: |  -  | *Indicates that the http connection must be upgraded.*                                      |
      | `Upgrade`         |               str               | :ballot_box_with_check: |  -  | *Upgrade string transmitted with this request.*                                             |
      | `Content`         |        memoryview or None       | :ballot_box_with_check: |  -  | *Raw data of the content included in this request.*                                         |
      | `Response`        | [HttpResponse](#response-class) | :ballot_box_with_check: |  -  | *Http response related to this connection.*                                                 |
      | `XAsyncTCPClient` |         XAsyncTCPClient         | :ballot_box_with_check: |  -  | *Asynchronous TCP connection from the XAsyncSockets library.*                               |

  <a name="response-class"></a>
  - ## HttpResponse Class

    <a name="response-static-func"></a>
    - ### Static Methods

    <a name="response-func"></a>
    - ### Instance Methods

    <a name="response-prop"></a>
    - ### Properties

      | Name             |              Type             |           Get           |           Set           | Description                                                                                 |
      |------------------|:-----------------------------:|:-----------------------:|:-----------------------:|---------------------------------------------------------------------------------------------|
      | `Request`        | [HttpRequest](#request-class) | :ballot_box_with_check: |            -            | *Http request related to this response.*                                                    |
      | `UserAddress`    |             tuple             | :ballot_box_with_check: |            -            | *User remote address of the http connection such as a tuple of `(str_ip_addr, int_port)`.*  |
      | `IsSSL`          |              bool             | :ballot_box_with_check: |            -            | *Indicates that the http connection is secured by SSL/TLS security layer with certificate.* |
      | `AllowCaching`   |              bool             | :ballot_box_with_check: | :ballot_box_with_check: | *Indicates to the user the possible caching of this response.*                              |
      | `ContentType`    |          str or None          | :ballot_box_with_check: | :ballot_box_with_check: | *Type of the content of this response.*                                                     |
      | `ContentCharset` |          str or None          | :ballot_box_with_check: | :ballot_box_with_check: | *Encoding charset used for the content of this response.*                                   |
      | `ContentLength`  |              int              | :ballot_box_with_check: | :ballot_box_with_check: | *Length of the content of this response.*                                                   |
      | `HeadersSent`    |              bool             | :ballot_box_with_check: |            -            | *Indicates that response http headers was already sent.*                                    |

  <a name="modules"></a>
  - ## Additional modules

    <a name="websockets-mod"></a>
    - ## WebSockets Module

      <a name="websocket-class"></a>
      - ## WebSocket Class

        <a name="websocket-static-func"></a>
        - ### Static Methods

        <a name="websocket-func"></a>
        - ### Instance Methods

        <a name="websocket-prop"></a>
        - ### Properties

          | Name                   |                   Type                  |           Get           |           Set           | Description                                     |
          |------------------------|:---------------------------------------:|:-----------------------:|:-----------------------:|-------------------------------------------------|
          | `Request`              |     [ HttpRequest](#request-class)      | :ballot_box_with_check: |            -            | *Http request related to this connection.*      |
          | `IsClosed`             |                   bool                  | :ballot_box_with_check: |            -            | *Indicates that connection is closed.*          |
          | `WaitFrameTimeoutSec`  |                   int                   | :ballot_box_with_check: | :ballot_box_with_check: | *Timeout in seconds to waiting next frame.*     |
          | `MaxRecvMessageLength` |               int or None               | :ballot_box_with_check: | :ballot_box_with_check: | *Maximum length of messages to receive.*        |
          | `OnTextMessage`        |  [callback](#ws-ontextmessage) or None  | :ballot_box_with_check: | :ballot_box_with_check: | *Callback function to receive text messages.*   |
          | `OnBinaryMessage`      | [callback](#ws-onbinarymessage) or None | :ballot_box_with_check: | :ballot_box_with_check: | *Callback function to receive binary messages.* |
          | `OnClosed`             |     [callback](#ws-onclosed) or None    | :ballot_box_with_check: | :ballot_box_with_check: | *Callback function when connection is closed.*  |

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

<a name="author"></a>
## :wink: Author

  **Jean-Christophe Bos** (:fr:)
  - GitHub: *[@jczic](https://github.com/jczic)*
  - E-mail: *<jcb@hc2.fr>*
  - Web:    *[www.hc2.fr](https://www.hc2.fr)*

---

<a name="license"></a>
## :paperclip: License

  - Copyright :copyright: 2019 [Jean-Christophe Bos](https://www.linkedin.com/in/jczic) & [HC²](https://www.hc2.fr).
  - This project is [MIT](LICENSE) licensed.
