import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import PlacePeek from './PlacePeek.vue'

describe('PlacePeek', () => {
  it('renders building context and emits close', async () => {
    const wrapper = mount(PlacePeek, {
      props: { place: { name: '逸夫楼', category: 'TEACHING' } },
    })

    expect(wrapper.text()).toContain('逸夫楼')
    expect(wrapper.text()).toContain('教学建筑')
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(1)
  })
})
