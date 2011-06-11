from oempmwiki import util


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


class WikiTable(object):
    """
    A convenience object for creating general moin moin tables.
    """
    row_class = WikiRow

    def __init__(self, data, has_headers=False, has_subheaders=False, 
                 writer=None):
        self.headers = None
        self.subheaders = None
        self._process_headers(data, has_headers, has_subheaders)
        self.raw_rows = data
        self.rows = []
        self.writer = writer
        self._compile()

    def _process_headers(self, data, has_headers, has_subheaders):
        if has_headers:
            self.headers = ["'''%s'''" % x for x in data.pop(0)]
            if has_subheaders:
                self.subheaders = ["''%s''" % x for x in data.pop(0)]

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


class ProjectStatusRow(WikiRow):
    """
    A WikiRow subclass that has project-specific customizations.
    """
    def __init__(self, cells):
        super(ProjectStatusRow, self).__init__(cells)
        cells = []
        for cell in self.cells:
            # normalize the casing of the cell data
            if util.get_status(cell):
                cell = util.color_cell(cell)
            cells.append(cell)
            # add rules for coloring cells based on content
        self.cells = cells 


class ProjectStatusTable(WikiTable):
    """
    A WikiTable subclass that has project-specific customizations.
    """
    row_class = ProjectStatusRow
    # XXX add support for custom header and subheader colors

