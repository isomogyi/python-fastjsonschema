from .draft06 import CodeGeneratorDraft06


class CodeGeneratorDraft07(CodeGeneratorDraft06):
    def __init__(self, definition, resolver=None):
        super().__init__(definition, resolver)
        self._json_keywords_to_function.update((
            ('if', self.generate_if_then_else),
            ('contentEncoding', self.generate_content_encoding),
            ('contentMediaType', self.generate_content_media_type),
        ))

    def generate_if_then_else(self):
        """
        Implementation of if-then-else.

        .. code-block:: python

            {
                'if': {
                    'exclusiveMaximum': 0,
                },
                'then': {
                    'minimum': -10,
                },
                'else': {
                    'multipleOf': 2,
                },
            }

        Valid values are any between -10 and 0 or any multiplication of two.
        """
        with self.l('try:'):
            self.generate_func_code_block(
                self._definition['if'],
                self._variable,
                self._variable_name,
                clear_variables=True
            )
        with self.l('except JsonSchemaException:'):
            if 'else' in self._definition:
                self.generate_func_code_block(
                    self._definition['else'],
                    self._variable,
                    self._variable_name,
                    clear_variables=True
                )
            else:
                self.l('pass')
        if 'then' in self._definition:
            with self.l('else:'):
                self.generate_func_code_block(
                    self._definition['then'],
                    self._variable,
                    self._variable_name,
                    clear_variables=True
                )

    def generate_content_encoding(self):
        """
        Means decoding value when it's encoded by base64.

        .. code-block:: python

            {
                'contentEncoding': 'base64',
            }
        """
        if self._definition['contentEncoding'] == 'base64':
            with self.l('if isinstance({variable}, str):'):
                with self.l('try:'):
                    self.l('import base64')
                    self.l('{variable} = base64.b64decode({variable})')
                with self.l('except Exception:'):
                    self.l('raise JsonSchemaException("{name} must be encoded by base64")')
                with self.l('if {variable} == "":'):
                    self.l('raise JsonSchemaException("contentEncoding must be base64")')

    def generate_content_media_type(self):
        """
        Means loading value when it's specified as JSON.

        .. code-block:: python

            {
                'contentMediaType': 'application/json',
            }
        """
        if self._definition['contentMediaType'] == 'application/json':
            with self.l('if isinstance({variable}, bytes):'):
                with self.l('try:'):
                    self.l('{variable} = {variable}.decode("utf-8")')
                with self.l('except Exception:'):
                    self.l('raise JsonSchemaException("{name} must encoded by utf8")')
            with self.l('if isinstance({variable}, str):'):
                with self.l('try:'):
                    self.l('import json')
                    self.l('{variable} = json.loads({variable})')
                with self.l('except Exception:'):
                    self.l('raise JsonSchemaException("{name} must be valid JSON")')