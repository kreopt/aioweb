import os
from pathlib import Path

from aiohttp.log import web_logger
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_response import StreamResponse
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_urldispatcher import StaticResource, ResourceRoute, PrefixResource
from yarl import unquote, URL


class StaticMultidirResource(StaticResource):

    def __init__(self, prefix, directories, *, name=None,
                 expect_handler=None, chunk_size=256*1024,
                 response_factory=StreamResponse,
                 show_index=False, follow_symlinks=False):
        super(StaticResource, self).__init__(prefix, name=name)
        newdirs = []
        for directory in directories:
            try:
                directory = Path(directory)
                if str(directory).startswith('~'):
                    directory = Path(os.path.expanduser(str(directory)))
                directory = directory.resolve()
                if not directory.is_dir():
                    raise ValueError('Not a directory')
                newdirs.append(directory)
            except (FileNotFoundError, ValueError) as error:
                web_logger.warn("No directory exists at '{}'".format(directory))
                # raise ValueError(
                #     "No directory exists at '{}'".format(directory)) from error
        self._directories = newdirs
        self._show_index = show_index
        self._chunk_size = chunk_size
        self._follow_symlinks = follow_symlinks
        self._expect_handler = expect_handler

        self._routes = {'GET': ResourceRoute('GET', self._handle, self,
                                             expect_handler=expect_handler),

                        'HEAD': ResourceRoute('HEAD', self._handle, self,
                                              expect_handler=expect_handler)}

    def get_info(self):
        return {'directories': self._directories,
                'prefix': self._prefix}

    async def _handle(self, request):
        filename = unquote(request.match_info['filename'])
        filepath = None
        for directory in self._directories:
            try:
                filepath = directory.joinpath(filename).resolve()
                if not self._follow_symlinks:
                    filepath.relative_to(directory)
            except (ValueError, FileNotFoundError) as error:
                # relatively safe
                pass
            except Exception as error:
                # perm error or other kind!
                request.app.logger.exception(error)

        if not filepath:
            raise HTTPNotFound()

        # on opening a dir, load it's contents if allowed
        if filepath.is_file():
            ret = FileResponse(filepath, chunk_size=self._chunk_size)
        else:
            raise HTTPNotFound

        return ret


    def __repr__(self):
        name = "'" + self.name + "'" if self.name is not None else ""
        return "<StaticMultiResource {name} {path} -> [{directory!r}]".format(
            name=name, path=self._prefix, directory='; '.join([str(e) for e in self._directories]))
