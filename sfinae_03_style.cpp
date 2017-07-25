#include <iostream>

template<typename T, typename RET_T = void, typename... ARGS>
struct has_foo
{
	template<typename U, RET_T(U::*)(ARGS...) const> struct sfinae_const_impl {};
	template<typename U, RET_T(U::*)(ARGS...)> struct sfinae_non_const_impl {};
	template<typename U> static char 
		test_const(sfinae_const_impl<U, &U::foo>*);
	template<typename U> static char
		test_non_const(sfinae_non_const_impl<U, &U::foo>*);
	template<typename U> static int
		test_const(...);
	template<typename U> static int
		test_non_const(...);
public:
	static const bool value = (sizeof(test_const<T>(0)) == sizeof(char) || sizeof(test_non_const<T>(0)) == sizeof(char));
};

class PORT;
class INST_PORT;

class FOO
{
public:
	bool foo(const PORT* p, const INST_PORT* ip) const { return true;  }
	bool foo(const PORT* p) { return true; }
	void foo() {}
};

int main()
{
	std::cout << has_foo<FOO>::value << "\n";
	return 0;
}