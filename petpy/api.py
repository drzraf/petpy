# encoding=utf-8


from pandas import DataFrame
from pandas.io.json import json_normalize
import requests
from urllib.parse import urljoin


class Petfinder(object):
    r"""
    Wrapper class for the PetFinder API.

    Attributes
    ----------
    host : str
        The base URL of the Petfinder API.
    key : str
        The API key.
    secret: str
        The secret key.

    Methods
    -------
    animal_types(types, return_df=False)
        Returns data on an animal type, or types available from the PetFinder API.

    """
    def __init__(self, key, secret):
        r"""

        Parameters
        ----------
        key : str
            API key given after `registering on the PetFinder site <https://www.petfinder.com/developers/api-key>`_
        secret : str
            Secret API key given in addition to general API key. The secret key is required as of V2 of
            the PetFinder API and is obtained from the Petfinder website at the same time as the access key.

        """
        self.key = key
        self.secret = secret
        self.host = 'http://api.petfinder.com/v2/'
        self.auth = self._authenticate()

        self._animal_types = ('dog', 'cat', 'rabbit', 'small-furry',
                                 'horse', 'bird', 'scales-fins-other', 'barnyard')

    def _authenticate(self):
        r"""
        Internal function for authenticating users to the Petfinder API.

        Raises
        ------
        HTTPError
            Raised when the authentication to the Petfinder API is unsuccessful.

        Returns
        -------
        str
            Access token granted by the Petfinder API. The access token stays live for 3600 seconds, or one hour,
            at which point the user must reauthenticate.

        """
        endpoint = 'oauth2/token'

        url = urljoin(self.host, endpoint)

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.key,
            'client_secret': self.secret
        }

        r = requests.post(url, data=data)

        if r.status_code != 200:
            raise requests.exceptions.HTTPError(r.reason)

        if r.json()['token_type'] == 'Bearer':
            return r.json()['access_token']

        else:
            raise requests.exceptions.HTTPError('could not authenticate to the PetFinder API')

    def animal_types(self, types=None):
        r"""
        Returns data on an animal type, or types available from the PetFinder API. This data includes the
        available type's coat names and colors, gender and other specific information relevant to the
        specified type(s). The animal type must be of 'dog', 'cat', 'rabbit', 'small-furry', 'horse', 'bird',
        'scales-fins-other', 'barnyard'.

        Parameters
        ----------
        types : str, list or tuple, optional
            Specifies the animal type or types to return. Can be a string representing a single animal type, or a
            tuple or list of animal types if more than one type is desired. If not specified, all animal types are
            returned.

        Raises
        ------
        ValueError
            Raised when the :code:`types` parameter receives an invalid animal type.
        TypeError
            If the :code:`types` is not given either a str, list or tuple, or None, a :code:`TypeError` will be
            raised.

        Returns
        -------
        json or pandas DataFrame

        Examples
        --------

        """

        if types is None:
            url = urljoin(self.host, 'types')

            r = requests.get(url, headers={
                'Authorization': 'Bearer ' + self.auth,
            })

            result = r.json()

        elif isinstance(types, str):
            if str.lower(types) not in self._animal_types:
                raise ValueError('type must be one of "dog", "cat", "rabbit", "small-furry", "horse", '
                                 '"bird", "scales-fins-others", "barnyard"')
            else:
                url = urljoin(self.host, 'types/{type}'.format(type=types))

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 })

                result = r.json()

        elif isinstance(types, (tuple, list)):
            types_check = list(set(types).difference(self._animal_types))

            if len(types_check) >= 1:
                unknown_types = ', '.join(types_check)

                raise ValueError('animal types {types} not available. Must be one of "dog", "cat", "rabbit", '
                                 '"small-furry", "horse", "bird", "scales-fins-others", "barnyard"'
                                 .format(types=unknown_types))

            else:
                types_collection = []

                for type in types:
                    url = urljoin(self.host, 'types/{type}'.format(type=type))

                    r = requests.get(url,
                                     headers={
                                         'Authorization': 'Bearer ' + self.auth
                                     })

                    types_collection.append(r.json()['type'])

            result = {'types': types_collection}

        else:
            raise TypeError('types parameter must be either None, str, list or tuple')

        return result

    def breeds(self, types=None, return_df=False, raw_results=False):
        r"""
        Returns breed names of specified animal type or types.

        Parameters
        ----------
        types :  str, list or tuple, optional
            String representing a single animal type or a list or tuple of a collection of animal types. If not
            specified, all available breeds for each animal type is returned. The animal type must be of 'dog',
            'cat', 'rabbit', 'small-furry', 'horse', 'bird', 'scales-fins-other', 'barnyard'.
        return_df : boolean, default False
            If :code:`True`, the result set will be coerced into a pandas :code:`DataFrame` with two columns,
            breed and name. If :code:`return_df` is set to :code:`True`, it will override the :code:`raw_result`
            parameter if it is also set to :code:`True` and return a pandas :code:`DataFrame`.
        raw_results: boolean, default False
            The PetFinder API :code:`breeds` endpoint returns some extraneous data in its result set along with the
            breed names of the specified animal type(s). If :code:`raw_results` is :code:`False`, the method will
            return a cleaner JSON object result set with the extraneous data removed. This parameter can be set to
            :code:`True` for those interested in retrieving the entire result set. If the parameter :code:`return_df`
            is set to :code:`True`, a pandas :code:`DataFrame` will be returned regardless of the value specified for
            the :code:`raw_result` parameter.

        Raises
        ------
        ValueError
            Raised when the :code:`types` parameter receives an invalid animal type.
        TypeError
            If the :code:`types` is not given either a str, list or tuple, or None, a :code:`TypeError` will be
            raised.

        Returns
        -------
        json or pandas DataFrame

        Examples
        --------

        """
        if types is None or isinstance(types, (list, tuple)):
            if types is None:
                types = self._animal_types

            else:
                types_check = list(set(types).difference(self._animal_types))

                if len(types_check) >= 1:
                    unknown_types = ', '.join(types_check)

                    raise ValueError('animal types {types} not available. Must be one of "dog", "cat", "rabbit", '
                                     '"small-furry", "horse", "bird", "scales-fins-others", "barnyard"'
                                     .format(types=unknown_types))

            breeds = []

            for t in types:
                url = urljoin(self.host, 'types/{type}/breeds'.format(type=t))

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 })

                breeds.append({t: r.json()})

            result = {'breeds': breeds}

        elif isinstance(types, str):
            if str.lower(types) not in self._animal_types:
                raise ValueError('type must be one of "dog", "cat", "rabbit", "small-furry", "horse", '
                                 '"bird", "scales-fins-others", "barnyard"')

            url = urljoin(self.host, 'types/{type}/breeds'.format(type=types))

            r = requests.get(url,
                             headers={
                                 'Authorization': 'Bearer ' + self.auth
                             })

            result = r.json()

        else:
            raise TypeError('types parameter must be either None, str, list or tuple')

        if return_df:
            raw_results = True

            df_results = DataFrame()

            if isinstance(types, (tuple, list)):

                for t in range(0, len(types)):
                    df_results = df_results.append(json_normalize(result['breeds'][t][types[t]]['breeds']))

            else:
                df_results = df_results.append(json_normalize(result['breeds']))

            df_results.rename(columns={'_links.type.href': 'breed'}, inplace=True)
            df_results['breed'] = df_results['breed'].str.replace('/v2/types/', '').str.capitalize()

            result = df_results

        if not raw_results:

            json_result = {
                'breeds': {

                }
            }

            if isinstance(types, (tuple, list)):
                for t in range(0, len(types)):
                    json_result['breeds'][types[t]] = []

                    for breed in result['breeds'][t][types[t]]['breeds']:
                        json_result['breeds'][types[t]].append(breed['name'])

            else:
                json_result['breeds'][types] = []

                for breed in result['breeds']:
                    json_result['breeds'][types].append(breed['name'])

            result = json_result

        return result

    def animals(self, animal_id=None, type=None, breed=None, size=None, gender=None,
                age=None, color=None, coat=None, status=None, name=None,
                organization=None, location=None, distance=None, sort=None, results=20, return_df=False):
        r"""

        Parameters
        ----------
        animal_id : optional
        type : optional
        breed: optional
        size: optional
        gender : optional
        age : optional
        color : optional
        coat : optional
        status : optional
        name : optional
        organization : optional
        location : optional
        distance : optional
        sort : optional
        results : default 20
        return_df : boolean, default False


        Raises
        ------

        Returns
        -------
        dict or pandas DataFrame

        """
        pass

    def organizations(self, organization_id=None, name=None, location=None, distance=None, state=None,
                     country=None, query=None, sort=None, results_per_page=20, pages=None, return_df=False):
        r"""

        Parameters
        ----------
        organization_id : optional
        name : optional
        location : optional
        distance : optional
        state : optional
        country : optional
        query : optional
        sort : optional
        pages : default 1
        results_per_page : int, default 20
        return_df : boolean, default False

        Raises
        ------
        TypeError


        Returns
        -------
        dict or pandas DataFrame

        """
        max_page_warning = False

        if organization_id is not None:

            url = urljoin(self.host, 'organizations/{id}')

            if isinstance(organization_id, (tuple, list)):

                organizations = []

                for org_id in organization_id:
                    r = requests.get(url.format(id=org_id),
                                     headers={
                                         'Authorization': 'Bearer ' + self.auth
                                     })

                    organizations.append(r.json())

            else:
                r = requests.get(url.format(id=organization_id),
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 })

                organizations = r.json()

        else:

            url = urljoin(self.host, 'organizations/')

            params = _parameters(name=name, location=location, distance=distance,
                                 state=state, country=country, query=query, sort=sort,
                                 results_per_page=results_per_page)

            if pages is None:

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 },
                                 params=params)
                
                organizations = r.json()['organizations']
                
            elif pages is not None:
                params['page'] = 1

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 },
                                 params=params)

                organizations = r.json()['organizations']

                max_pages = r.json()['pagination']['total_pages']

                if pages > int(max_pages):
                    pages = max_pages
                    max_page_warning = True

                for page in range(2, pages):

                    params['page'] = page

                    r = requests.get(url,
                                     headers={
                                         'Authorization': 'Bearer ' + self.auth
                                     },
                                     params=params)

                    for i in r.json()['organizations']:
                        organizations.append(i)

            elif results_per_page is None:

                params['results'] = 100

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 },
                                 params=params)

                pagination = r.json()['pagination']['total_pages']

                organizations = r.json()['organizations']

                for p in range(2, pagination):
                    params['page'] = p

                    r = requests.get(url,
                                     headers={
                                         'Authorization': 'Bearer ' + self.auth
                                     },
                                     params=params)

                    for i in r.json()['organizations']:
                        organizations.append(i)

            else:
                raise TypeError('parameter results must be an integer or None.')

        if return_df:
            organizations = DataFrame(organizations)

        if max_page_warning:
            print('pages parameter exceeded maximum number of available pages available from the Petfinder API. As '
                  'a result, the maximum number of pages {max_page} was returned'.format(max_page=max_pages))

        return organizations


def _parameters(animal=None, breed=None, size=None, sex=None, location=None, distance=None, state=None,
                country=None, query=None, sort=None, name=None, age=None, animal_id=None, organization_id=None,
                status=None, results_per_page=None, page=None):

    args = {
        'animal': animal,
        'breed': breed,
        'size': size,
        'sex': sex,
        'age': age,
        'location': location,
        'distance': distance,
        'state': state,
        'country': country,
        'query': query,
        'sort': sort,
        'name': name,
        'animal_id': animal_id,
        'organization_id': organization_id,
        'status': status,
        'limit': results_per_page,
        'page': page
    }

    args = {key: val for key, val in args.items() if val is not None}

    return args
