# -*- coding: utf-8 -*-

from proxypool.api import app
from proxypool.schedule import Schedule


def main():
    Schedule().run()
    app.run()


if __name__ == '__main__':
    main()
