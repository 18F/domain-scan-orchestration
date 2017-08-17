# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from typing import Tuple
from typing import Any
from nassl import _nassl
from typing import Dict
from typing import Text


class OcspResponseNotTrustedError(IOError):

    def __init__(self, trust_store_path):
        # type: (Text) -> None
        self.trust_store_path = trust_store_path


class OcspResponse(object):
    """High level API for parsing an OCSP response.
    """

    def __init__(self, ocsp_response):
        # type: (_nassl.OCSP_RESPONSE) -> None
        self._ocsp_response = ocsp_response
        self._ocsp_response_dict = None

    def as_text(self):
        # type: () -> Text
        return self._ocsp_response.as_text()

    def verify(self, verify_locations):
        # type: (Text) -> None
        """Verify that the OCSP response is trusted.

        Args:
            verify_locations: The file path to a trust store containing pem-formatted certificates, to be used for
            validating the OCSP response.

        Raises OcspResponseNotTrustedError if the validation failed ie. the OCSP response is not trusted.
        """
        # Ensure the file exists
        with open(verify_locations):
            pass

        try:
            self._ocsp_response.basic_verify(verify_locations)
        except _nassl.OpenSSLError as e:
            if 'certificate verify error' in str(e):
                raise OcspResponseNotTrustedError(verify_locations)
            raise


    def as_dict(self):
        # type: () -> Dict[Text, Any]
        if self._ocsp_response_dict:
            return self._ocsp_response_dict

        # For now we just parse OpenSSL's text output and make a lot of assumptions
        response_text = self.as_text()
        response_dict = {
            'responseStatus': self._get_value_from_text_output_no_p('OCSP Response Status:', response_text),
            'version' : self._get_value_from_text_output_no_p('Version:', response_text),
            'responseType': self._get_value_from_text_output('Response Type:', response_text),
            'responderID': self._get_value_from_text_output('Responder Id:', response_text),
            'producedAt': self._get_value_from_text_output('Produced At:', response_text),
            }
        if 'successful' not in response_dict['responseStatus']:
            return response_dict

        # TODO(ad): This will not work correctly if there are multiple responses as it assumes just one
        response_dict['responses'] = [
            {
                'certID': {
                    'hashAlgorithm': self._get_value_from_text_output('Hash Algorithm:', response_text),
                    'issuerNameHash': self._get_value_from_text_output('Issuer Name Hash:', response_text),
                    'issuerKeyHash': self._get_value_from_text_output('Issuer Key Hash:', response_text),
                    'serialNumber': self._get_value_from_text_output('Serial Number:', response_text)
                },
                'certStatus': self._get_value_from_text_output('Cert Status:', response_text),
                'thisUpdate': self._get_value_from_text_output('This Update:', response_text),
                'nextUpdate': self._get_value_from_text_output('Next Update:', response_text),
            }
        ]
        if self._get_scts_from_text_output(response_text):
            # SCT extension present
            response_dict['responses'][0]['singleExtensions'] = {'ctCertificateScts':
                                                                     self._get_scts_from_text_output(response_text)}

        self._ocsp_response_dict = response_dict
        return response_dict

# Text parsing
    @staticmethod
    def _get_value_from_text_output(key, text_output):
        # type: (Text, Text) -> Text
        value = text_output.split(key)
        return value[1].split('\n')[0].strip()

    @staticmethod
    def _get_value_from_text_output_no_p( key, text_output):
        # type: (Text, Text) -> Text
        value = text_output.split(key)
        value = value[1].split('\n')[0].strip()
        return value.split('(')[0].strip()

    @staticmethod
    def _parse_sct_text_line(text_output):
        # type: (Text, Text) -> Tuple[Text, Text]
        text_output_split = text_output.split(':', 1)
        key = text_output_split[0].strip()
        value = text_output_split[1].strip()
        if value == 'none':
            value = None
        return key, value

    @classmethod
    def _parse_single_sct(cls, sct_text_output):
        parsed_sct = {}
        for line in sct_text_output.split('\n'):
            # One-line fields
            if any(key in line for key in ['Version', 'Extensions', 'Timestamp']):
                key, value = cls._parse_sct_text_line(line)
                parsed_sct[key] = value

            elif 'Log ID' in line:
                log_id_text = sct_text_output.split('Log ID    :')[1].split('Timestamp')[0]
                final_log_id = ''
                for line in log_id_text:
                    final_log_id += line.strip(' ').replace('\n', '')
                parsed_sct['logId'] = final_log_id

        return parsed_sct

    @classmethod
    def _get_scts_from_text_output(cls, response_text):
        scts_text_list = response_text.split('Signed Certificate Timestamp')
        if len(scts_text_list) < 1:
            return None

        scts_text_list = scts_text_list[1::]
        parsed_scts = []
        for sct_text in scts_text_list:
            parsed_scts.append(cls._parse_single_sct(sct_text))
        return parsed_scts

