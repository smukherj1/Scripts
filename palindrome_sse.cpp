#include <string>
#include <iostream>
#include <tmmintrin.h>
#include <cassert>
#include <cstdint>

namespace
{
	__m128i s_reverse_shuffle_mask = _mm_set_epi8(
		0x00,
		0x01,
		0x02,
		0x03,
		0x04,
		0x05,
		0x06,
		0x07,
		0x08,
		0x09,
		0x0A,
		0x0B,
		0x0C,
		0x0D,
		0x0E,
		0x0F
	);

	inline bool is_palindrome_fallback(const char* c_str, unsigned int size)
	{
		auto cur = c_str;
		auto end = c_str + size - 1;
		while (cur < end)
		{
			if (*cur != *end)
			{
				return false;
			}
			++cur;
			--end;
		}
		return true;
	}

	// Return true if the given string with the given size is a palindrome
	inline bool is_palindrome(const char* c_str, unsigned int size)
	{
		assert(((uint64_t)c_str & 0xf) == 0);
		auto lhs_candidate = c_str;
		auto rhs_candidate = c_str + size - 16;
		// While string size is bigger than or equal to 32
		// check if the first 16 characters is the same as the
		// reversed version of the last 16 characters
		while (size >= 32)
		{
			// Address better be 16 byte aligned lulz
			// Load first 16 characters
			__m128i lhs_16chars = _mm_load_si128((const __m128i*)lhs_candidate);
			// Unaligned load
			// Load last 16 characters
			__m128i rhs_16chars = _mm_loadu_si128((const __m128i*)rhs_candidate);
			// Reverse the last 16 characters
			rhs_16chars = _mm_shuffle_epi8(rhs_16chars, s_reverse_shuffle_mask);
			// Compare the first 16 with the reversed version of the last 16
			__m128i vcmp = _mm_cmpeq_epi32(lhs_16chars, rhs_16chars);
			// If there's any mismatch, it means this string can't be a
			// palindrome. Return immediately
			uint16_t mask = _mm_movemask_epi8(vcmp);
			if (mask != 0xffff)
			{
				return false;
			}

			lhs_candidate += 16;
			rhs_candidate -= 16;
			size -= 32;
		}
		// Do character by character comparison for any remaining part of the
		// sequence shorter than 32 characters. Technically we could fall back twice
		// more, one that compares 8 packs of characters and another that does 4?
		return is_palindrome_fallback(lhs_candidate, size);
	}
}

int main()
{
	std::string foo = "abcdefghijklmnopcocponmlkjihgfedcba";
	is_palindrome(foo.c_str(), foo.size());
	return 0;
}