# microWebSrv2

![Release](https://img.shields.io/github/v/release/jczic/microwebsrv2?include_prereleases&color=success)
![Size](https://img.shields.io/github/languages/code-size/jczic/microwebsrv2?color=blue)
![MicroPython](https://img.shields.io/badge/micropython-Ok-green.svg)
![Python](https://img.shields.io/badge/python-Ok-green.svg)
![License](https://img.shields.io/github/license/jczic/microwebsrv2?color=yellow)

---

<br />

**MicroWebSrv2** is the new powerful embedded Web Server for **MicroPython** and **CPython** that supports **route handlers**, modules like **WebSockets** or **PyhtmlTemplate** and a **lot of simultaneous requests** (in thousands!).

**Fully asynchronous**, its connections and memory management are **very optimized** and **truly fast**.

Mostly used on **Pycom WiPy**, **ESP32**, **STM32** on **Pyboard**, ... **Robust** and **efficient**! (see [Features](#features))

#### [microWebSrv on GitHub](https://github.com/jczic/MicroWebSrv)

<br />

---

<br />

# About

This project follows the embedded [MicroWebSrv](https://github.com/jczic/MicroWebSrv),
which is mainly used on microcontrollers such as Pycom, ESP32 and STM32 on Pyboards.

In a need for scalability and to meet the IoT universe, **microWebSrv2** was developed as a new project
and has been completely redesigned to be much more robust and efficient that its predecessor.

Internal mechanisms works **directly at I/O level**, are fully asynchronous from end to end, and manages the memory in a highly optimized way.  
Also, architecture makes its integration very easy and the source code, **MIT licensed**, remains really small.

---

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

- Verify that a request is successfully **authenticated** by the **Basic** or **Bearer** method.

- Reduce the number of persistent connections per web client with **keep-alive mode** support.

- Respond to a request by using a **data stream** as content, sent with known length or in **chunked transfer-encoding**.

- Use a file to respond to a request that will be treated as **on-the-fly content** or as an **attachment to download**.

- Take advantage of the **WebSockets module** to exchange messages in real time via **WS or secured WSS** connection.

- Create **.pyhtml pages** for an HTML rendering with integrated Python using the **PyhtmlTemplate module**.

---

## Author

  **Jean-Christophe Bos**
  - GitHub: *[@jczic](https://github.com/jczic)*
  - Email:  *<jcb@hc2.fr>*
  - Web:    *[www.hc2.fr](https://www.hc2.fr)*

---

## License

  - Copyright :copyright: 2019 [Jean-Christophe Bos](https://www.linkedin.com/in/jczic) & [HC²](https://www.hc2.fr).
  - This project is [MIT](LICENSE) licensed.

---

<br />
<br />

![microWebSrv2](/img/microWebSrv2.png "microWebSrv2")
