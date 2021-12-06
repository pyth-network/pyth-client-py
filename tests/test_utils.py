from _pytest.logging import LogCaptureFixture
import pytest

from pytest_mock import MockerFixture

from mock import Mock

import dns.resolver
import dns.rdatatype
import dns.rdataclass
import dns.message
import dns.rrset
import dns.flags

from pythclient.utils import get_key


@pytest.fixture()
def answer_program() -> dns.resolver.Answer:
    qname = dns.name.Name(labels=(b'devnet-program-v2', b'pyth', b'network', b''))
    rdtype = dns.rdatatype.TXT
    rdclass = dns.rdataclass.IN
    response = dns.message.QueryMessage(id=0)
    response.flags = dns.flags.QR
    rrset_qn = dns.rrset.from_text(qname, 100, rdclass, rdtype)
    rrset_ans = dns.rrset.from_text(qname, 100, rdclass, rdtype, '"program=gSbePebfvPy7tRqimPoVecS2UsBvYv46ynrzWocc92s"')
    response.question = [rrset_qn]
    response.answer = [rrset_ans]
    answer = dns.resolver.Answer(
        qname=qname, rdtype=rdtype, rdclass=rdclass, response=response)
    answer.rrset = rrset_ans
    return answer


@pytest.fixture()
def answer_mapping() -> dns.resolver.Answer:
    qname = dns.name.Name(labels=(b'devnet-mapping-v2', b'pyth', b'network', b''))
    rdtype = dns.rdatatype.TXT
    rdclass = dns.rdataclass.IN
    response = dns.message.QueryMessage(id=0)
    response.flags = dns.flags.QR
    rrset_qn = dns.rrset.from_text(qname, 100, rdclass, rdtype)
    rrset_ans = dns.rrset.from_text(qname, 100, rdclass, rdtype, '"mapping=BmA9Z6FjioHJPpjT39QazZyhDRUdZy2ezwx4GiDdE2u2"')
    response.question = [rrset_qn]
    response.answer = [rrset_ans]
    answer = dns.resolver.Answer(
        qname=qname, rdtype=rdtype, rdclass=rdclass, response=response)
    answer.rrset = rrset_ans
    return answer


@pytest.fixture()
def mock_dns_resolver_resolve(mocker: MockerFixture) -> Mock:
    mock = Mock()
    mocker.patch('dns.resolver.resolve', side_effect=mock)
    return mock


def test_utils_get_program_key(mock_dns_resolver_resolve: Mock, answer_program: dns.resolver.Answer) -> None:
    mock_dns_resolver_resolve.return_value = answer_program
    program_key = get_key("devnet", "program")
    assert program_key == "gSbePebfvPy7tRqimPoVecS2UsBvYv46ynrzWocc92s"


def test_utils_get_mapping_key(mock_dns_resolver_resolve: Mock, answer_mapping: dns.resolver.Answer) -> None:
    mock_dns_resolver_resolve.return_value = answer_mapping
    mapping_key = get_key("devnet", "mapping")
    assert mapping_key == "BmA9Z6FjioHJPpjT39QazZyhDRUdZy2ezwx4GiDdE2u2"


def test_utils_get_mapping_key_not_found(mock_dns_resolver_resolve: Mock,
                                         answer_mapping: dns.resolver.Answer,
                                         caplog: LogCaptureFixture) -> None:
    mock_dns_resolver_resolve.side_effect = dns.resolver.NXDOMAIN
    exc_message = f'TXT record for {str(answer_mapping.response.canonical_name())[:-1]} not found'
    key = get_key("devnet", "mapping")
    assert exc_message in caplog.text
    assert key == ""


def test_utils_get_mapping_key_invalid_number(mock_dns_resolver_resolve: Mock,
                                              answer_mapping: dns.resolver.Answer,
                                              caplog: LogCaptureFixture) -> None:
    answer_mapping.rrset = None
    mock_dns_resolver_resolve.return_value = answer_mapping
    exc_message = f'Invalid number of records returned for {str(answer_mapping.response.canonical_name())[:-1]}!'
    key = get_key("devnet", "mapping")
    assert exc_message in caplog.text
    assert key == ""
