class WikiRawLine(object):
    """ 
    An object that simply holds a raw wiki line for later use.
    """
    split_on = "||"

    def __init__(self, line):
        self.line = line

    def render(self):
        return self.line


class WikiRow(WikiRawLine):
    """ 
    A convenience object for creating general moin moin table rows.
    """
    def __init__(self, cells):
        super(WikiRow, self).__init__(cells)
        self.cells = [unicode(x) for x in cells]

    def join(self):
        return "%s%s%s" % ( 
            self.split_on,
            self.split_on.join(self.cells),
            self.split_on)

    def render(self):
        return self.join()


class ProjectStatusRow(WikiRow):
    """
    A WikiRow subclass that has project-specific customizations.
    """
    # XXX add rules for checking/normalizing content
    # XXX add rules for coloring cells based on content


class WikiTable(object):
    """
    A convenience object for creating general moin moin tables.
    """
    def __init__(self, data, has_headers=False, has_subheaders=False, 
                 row_class=None, writer=None):
        self.headers = None
        self.subheaders = None
        self._process_headers(data, has_headers, has_subheaders)
        self.raw_rows = data
        self.rows = []
        self.writer = writer
        if not row_class:
            row_class = ProjectStatusRow
        self.row_class = row_class
        self._compile()

    def _process_headers(self, data, has_headers, has_subheaders):
        if has_headers:
            self.headers = data.pop(0)
            if has_subheaders:
                self.subheaders = data.pop(0)

    def _compile(self):
        if self.headers:
            self.rows.append(self.row_class(self.headers))
            if self.subheaders:
                self.rows.append(self.row_class(self.subheaders))
        for row_data in self.raw_rows:
            self.rows.append(self.row_class(row_data))

    def render(self):
        return "\n".join([x.render() for x in self.rows])

    def write(self, writer=None):
        if writer:
            self.writer = writer
        self.writer.write(self.render())

 
class ProjectStatusTable(WikiTable):
    """
    A WikiTable subclass that has project-specific customizations.
    """
    # XXX add support for custom header and subheader colors

