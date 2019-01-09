import React from 'react';
import { shallow } from 'enzyme';
import UsersList from '../UsersList';
import renderer from 'react-test-renderer';

const users = [
  {
    'active': true,
    'email': 'potato@example.com',
    'id': 1,
    'username': 'potato'
  },
  {
    'active': true,
    'email': 'chip@example.com',
    'id': 2,
    'username': 'chip'
  }
];

test('UsersList renders properly', () => {
  const wrapper = shallow(<UsersList users={users}/> );
  const element = wrapper.find('h4');
  expect(element.length).toBe(2);
  //console.log(element.get(0).props.children[1]);
  expect(element.get(0).props.children).toBe('potato');
});


test('UsersList renders a snapshot properly', () => {
  const tree = renderer.create(<UsersList users={users} />).toJSON();
  expect(tree).toMatchSnapshot();
});
