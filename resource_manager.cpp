#include <iostream>
#include <memory>
#include <vector>
#include <utility>
#include <tuple>
#include <algorithm>
#include <mutex>

template <
	class K, 
	class V,
	class KeyEquals = std::equal_to<K>
>
class SharedResourceManager
{
public:
	template
	<typename... Args>
	std::shared_ptr<V> obtain(K key, Args&&... args)
	{
		std::lock_guard<std::mutex> lock(m_mutex);
		auto it = std::find_if(
			m_resources.begin(),
			m_resources.end(),
			[key, this](const value_type& iv)
		{
			return m_key_equals(std::get<0>(iv), key);
		}
		);

		// Resource didn't exist. Allocate new one
		// and own it by default
		if (it == m_resources.end())
		{
			res_shared_ptr new_owned_resource = std::make_shared<V>(std::forward<Args>(args)...);
			res_weak_ptr unowned_res = new_owned_resource;
			m_resources.emplace_back(
				std::make_tuple(
					key,
					new_owned_resource,
					unowned_res
				)
			);
			return new_owned_resource;
		}

		value_type& val = *it;
		res_shared_ptr& result = std::get<1>(val);
		// This resource is still owned by this manager!
		if (result)
		{
			return result;
		}

		// Ok the resource isn't owned by this manager.
		// Try to see if the weak pointer can be promoted
		// ie. The object is still alive somewhere
		res_weak_ptr& weak_res = std::get<2>(val);
		result = weak_res.lock();
		if (result)
		{
			// Re-acquisition of ownership was a success!
			return result;
		}

		// Need to reallocate object. Weak pointer was invalid
		result = std::make_shared<V>(std::forward<Args>(args)...);
		weak_res = result;

		return result;
	}

	// Give up ownership of the object
	// corresponding to this key
	void relinquish(K key)
	{
		std::lock_guard<std::mutex> lock(m_mutex);
		auto it = std::find_if(
			m_resources.begin(),
			m_resources.end(),
			[key, this](const value_type& iv)
		{
			return m_key_equals(std::get<0>(iv), key);
		}
		);

		if (it != m_resources.end())
		{
			value_type& val = *it;
			res_shared_ptr owned_ptr = std::get<1>(val);
			owned_ptr.reset();
		}
	}

	// Givup and release all memory to the object
	// corresponding to this key
	// However, if someone outside this manager is
	// holding an active shared_ptr, the object
	// will continue to survive
	void unload(K key)
	{
		std::lock_guard<std::mutex> lock(m_mutex);
		auto it = std::remove_if(
			m_resources.begin(),
			m_resources.end(),
			[key, this](const value_type& iv)
		{
			return m_key_equals(std::get<0>(iv), key);
		}
		);

		m_resources.erase(it, m_resources.end());
	}

private:
	using res_weak_ptr = std::weak_ptr<V>;
	using res_shared_ptr = std::shared_ptr<V>;
	using value_type = std::tuple<K, res_shared_ptr, res_weak_ptr>;
	using collection_type = std::vector<value_type>;

	collection_type m_resources;
	std::mutex m_mutex;
	KeyEquals m_key_equals;
	
};


int main()
{
	SharedResourceManager<int, int> int_mgr;
	auto iptr = int_mgr.obtain(0, 1);
	std::cout << *iptr << "\n";
	return 0;
}
