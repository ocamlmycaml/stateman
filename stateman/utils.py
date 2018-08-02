from collections import defaultdict
from functools import wraps


global_transition_functions = defaultdict(lambda: defaultdict(dict))
global_validation_functions = defaultdict(list)


class Transitionable(object):
    """Behavior that allows a class to collect transitions"""

    @classmethod
    def register_transition(cls, from_, to):

        def decorator(func):
            """This decorates the function, but also registers the function in the class's transition_functions
            dictinoary as a transition to the new state"""

            if not to:
                raise ValueError("'to' state must be non-empty")

            from_state_key = tuple(sorted(from_.items()))
            to_state_key = tuple(sorted(to.items()))
            global_transition_functions[cls][from_state_key][to_state_key] = func

            @wraps(func)
            def new_func(item_self):
                """This is the replacement method. We're gonna assume the first arg is a node, and in most
                cases self. if that's not the case, we will throw an error

                Args:
                    item_self (Transitionable): item we are transitioning
                """
                if not isinstance(item_self, cls):
                    raise ValueError(f"You can only run this transitions for instances of {cls.__name__}")

                if not all(
                        from_key in item_self.state and from_value == item_self.state[from_key]
                        for from_key, from_value in from_.items()
                ):
                    raise ValueError(f"Your {cls.__name__} must contain this for transitioning: {from_}")

                # run function
                result = func(item_self)

                # update state
                state = {**item_self.state, **to}
                state = {key: value for key, value in state.items() if value is not None}
                item_self.state = state

                return result

            return new_func

        return decorator


class ValidationError(Exception):
    pass


class Validatable(object):
    """Behavior that allows validations to happen"""

    @classmethod
    def register_validation(cls, func):
        """This decorates the function, but also registers the function in the class's transition_functions
        dictinoary as a transition to the new state"""

        @wraps(func)
        def wrapper(node_self):
            """This is the replacement method. We're gonna assume the first arg is a node, and in most
            cases self. if that's not the case, we will throw an error

            Args:
                node_self (StateNode): node we are transitioning
            """
            if not isinstance(node_self, cls):
                raise ValueError(f"You can only define validations for instances of {cls.__name__}")

            func(node_self)

        global_validation_functions[cls].append(wrapper)
        return wrapper

    def validate(self):
        """returns validation results"""
        results = {}
        assert self.__class__ in global_validation_functions
        for validation_func in global_validation_functions[self.__class__]:
            try:
                validation_func(self)
            except Exception as e:
                results[validation_func.__name__] = e

        if any(results.values()):
            raise Exception(results)
