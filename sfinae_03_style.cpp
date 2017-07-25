#include <iostream>
#include <type_traits>

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
	bool foo(const PORT* p) 
	{ 
		std::cout << "FOO::foo(const PORT*) invoked\n";
		return true; 
	}
};

class BAR
{
public:
	void foo(int* goo) const { std::cout << "BAR::foo(int*) invoked\n"; }
};

class BAZ
{
public:
	void wut() const {}
};

template
<class T, typename = void>
struct CALLBACK_IMPL
{
	static void call(T& t) { std::cout << "Default CALLBACK_IMPL invoked\n"; }
};

template
<class T>
struct CALLBACK_IMPL<T, typename std::enable_if<has_foo<T, void, int*>::value>::type>
{
	static void call(T& t) { t.foo(nullptr); }
};

template
<class T>
class CALLBACK
{
public:
	void call() const { CALLBACK_IMPL<T>::call(T()); }
};


int main()
{
	CALLBACK<FOO> cf;
	cf.call();
	CALLBACK<BAR> bf;
	bf.call();
	CALLBACK<BAZ> bzf;
	bzf.call();
	return 0;
}
