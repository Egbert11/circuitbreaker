from unittest.mock import Mock

from mock.mock import patch
from pytest import raises

from circuitbreaker import CircuitBreaker, CircuitBreakerError, circuit


def test_circuitbreaker__str__():
    cb = CircuitBreaker(name='Foobar')
    assert str(cb) == 'Foobar'


def test_circuitbreaker_error__str__():
    cb = CircuitBreaker(name='Foobar')
    cb._last_failure = Exception()
    error = CircuitBreakerError(cb)

    assert str(error).startswith('Circuit "Foobar" OPEN until ')
    assert str(error).endswith('(0 failures, 30 sec remaining) (last_failure: Exception())')


def test_circuitbreaker_should_save_last_exception_on_failure_call():
    cb = CircuitBreaker(name='Foobar')

    func = Mock(side_effect=IOError)

    with raises(IOError):
        cb.call(func)

    assert isinstance(cb.last_failure, IOError)


def test_circuitbreaker_should_clear_last_exception_on_success_call():
    cb = CircuitBreaker(name='Foobar')
    cb._last_failure = IOError()
    assert isinstance(cb.last_failure, IOError)

    cb.call(lambda: True)

    assert cb.last_failure is None


@patch('circuitbreaker.CircuitBreaker.decorate')
def test_circuit_decorator_without_args(circuitbreaker_mock):
    function = lambda: True
    circuit(function)
    circuitbreaker_mock.assert_called_once_with(function)


@patch('circuitbreaker.CircuitBreaker.__init__')
def test_circuit_decorator_with_args(circuitbreaker_mock):
    circuitbreaker_mock.return_value = None
    circuit(10, 20, KeyError, 'foobar')
    circuitbreaker_mock.assert_called_once_with(
        expected_exception=KeyError,
        failure_threshold=10,
        recovery_timeout=20,
        name='foobar'
    )
