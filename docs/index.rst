Flask-OpenID
============

.. module:: flask_openid

Flask-OpenID is an extension to `Flask`_ that allows you to add `OpenID`_
based authentication to your website in a matter of minutes.  It depends
on Flask and `python-openid`_ 2.x.  You can install the requirements from
PyPI with `easy_install` or `pip` or download them by hand.

Features
--------

- support for OpenID 2.x
- friendly API
- perfect integration into Flask
- basic support for AX and SReg extensions to OpenID that make it possible
  to fetch basic profile information from a user's OpenID provider.

Installation
------------

Install the extension with one of the following commands::

    $ easy_install Flask-OpenID

or alternatively if you have `pip` installed::

    $ pip install Flask-OpenID

How to Use
----------

To integrate Flask-OpenID into your application you need to create an
instance of the :class:`OpenID` object first::

    from flask.ext.openid import OpenID
    oid = OpenID(app, '/path/to/store', safe_roots=[])

By default it will use the filesystem as store for information needed by
OpenID for the authentication process.  You can alternatively implement
your own store that uses the database or a no-sql server.  For more
information about that, consult the python-openid documentation.

The path to the store can also be specified with the
``OPENID_FS_STORE_PATH`` configuration variable.

Alternatively the object can be instantiated without the application in
which case it can later be registered for an application with the
:meth:`~OpenID.init_app` method.

The list of URL roots that are safe to redirect the user to are passed via
`safe_roots`. Whenever the url root of the ``'next'`` request argument is not in
this list, the user will get redirected to the app root. All urls that are local
to the current app are always regared as trusted. This security mechanism
can be disabled by  leaving `safe_roots` out, but this is not suggested.

The current logged in user has to be memorized somewhere, we will use the
``'openid'`` key in the `session`.  This can be implemented in a
`before_request` function::

    from flask import g, session

    @app.before_request
    def lookup_current_user():
        g.user = None
        if 'openid' in session:
            openid = session['openid']
            g.user = User.query.filter_by(openid=openid).first()

This assumes the openid used for a user is stored in the user table
itself.  As you can see from the example above, we're using SQLAlchemy
here, but feel free to use a different storage backend.  It's just
important that you can somehow map from openid URL to user.

Next you need to define a login handling function.  This function is a
standard view function that is additionally decorated as
:meth:`~OpenID.loginhandler`::

    @app.route('/login', methods=['GET', 'POST'])
    @oid.loginhandler
    def login():
        if g.user is not None:
            return redirect(oid.get_next_url())
        if request.method == 'POST':
            openid = request.form.get('openid')
            if openid:
                return oid.try_login(openid, ask_for=['email', 'nickname'],
                                             ask_for_optional=['fullname'])
        return render_template('login.html', next=oid.get_next_url(),
                               error=oid.fetch_error())

What's happening inside the login handler is that first we try to figure
out if the user is already logged in.  In that case we return to where we
just came from (:meth:`~OpenID.get_next_url` can do that for us).  When
the data is submitted we get the openid the user entered and try to login
with that information.  Additionally we ask the openid provider for email,
nickname and the user's full name, where we declare full name as optional.
If that information is available, we can use it to simplify the account
creation process in our application.

The template also needs the URL we want to return to, because it has to
forward that information in the form.  If an error happened,
:meth:`~OpenID.fetch_error` will return that error message for us.

This is what a login template typically looks like:

.. sourcecode:: html+jinja

    {% extends "layout.html" %}
    {% block title %}Sign in{% endblock %}
    {% block body %}
      <h2>Sign in</h2>
      <form action="" method=post>
        {% if error %}<p class=error><strong>Error:</strong> {{ error }}</p>{% endif %}
        <p>
          OpenID:
          <input type=text name=openid size=30>
          <input type=submit value="Sign in">
          <input type=hidden name=next value="{{ next }}">
      </form>
    {% endblock %}

See how `error` and `next` are used.  The name of the form field `next` is
required, so don't change it.

Responding to Successful Logins
-------------------------------

Next we have to define a function that is called after the login was
successful.  The responsibility of that function is to remember the user
that just logged in and to figure out if it's a new user to the system or
one with an existing profile (if you want to use profiles).

Such a function is decorated with :meth:`~OpenID.after_login` and must
remember the user in the session and redirect to the proper page::

    from flask import flash

    @oid.after_login
    def create_or_login(resp):
        session['openid'] = resp.identity_url
        user = User.query.filter_by(openid=resp.identity_url).first()
        if user is not None:
            flash(u'Successfully signed in')
            g.user = user
            return redirect(oid.get_next_url())
        return redirect(url_for('create_profile', next=oid.get_next_url(),
                                name=resp.fullname or resp.nickname,
                                email=resp.email))

The `resp` object passed is a :class:`OpenIDResponse` object with all the
information you might desire.  As you can see, we memorize the user's
openid and try to get the user with that OpenID from the database.  If
that fails we redirect the user to a page to create a new profile and also
forward the name (or nickname if no name is provided) and the email
address.  Please keep in mind that an openid provider does not have to
support these profile information and not every value you ask for will be
there.  If it's missing it will be `None`.  Again make sure to not lose
the information about the next URL.

Creating a Profile
------------------

A typical page to create such a profile might look like this::

    @app.route('/create-profile', methods=['GET', 'POST'])
    def create_profile():
        if g.user is not None or 'openid' not in session:
            return redirect(url_for('index'))
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            if not name:
                flash(u'Error: you have to provide a name')
            elif '@' not in email:
                flash(u'Error: you have to enter a valid email address')
            else:
                flash(u'Profile successfully created')
                db_session.add(User(name, email, session['openid']))
                db_session.commit()
                return redirect(oid.get_next_url())
        return render_template('create_profile.html', next=oid.get_next_url())

If you're using the same names for the URL parameters in the step before
and in this form, you have nice looking and simple templates:

.. sourcecode:: html+jinja

    {% extends "layout.html" %}
    {% block title %}Create Profile{% endblock %}
    {% block body %}
      <h2>Create Profile</h2>
      <p>
        Hey!  This is the first time you signed in on this website.  In
        order to proceed we need a couple of more information from you:
      <form action="" method=post>
        <dl>
          <dt>Name:
          <dd><input type=text name=name size=30 value="{{ request.values.name }}">
          <dt>E-Mail:
          <dd><input type=text name=email size=30 value="{{ request.values.email }}">
        </dl>
        <p>
          <input type=submit value="Create profile">
          <input type=hidden name=next value="{{ next }}">
      </form>
      <p>
        If you don't want to proceed, you can <a href="{{ url_for('logout')
        }}">sign out</a> again.
    {% endblock %}

Logging Out
-----------

The logout function is very simple, it just has to unset the openid from
the session and redirect back to where the user was before::

    @app.route('/logout')
    def logout():
        session.pop('openid', None)
        flash(u'You were signed out')
        return redirect(oid.get_next_url())

Advanced usage
--------------

Flask-OpenID can also work with any python-openid extension.
To use this, pass a list of instantiated request openid.extension.Extension
objects in the `extensions` field of :meth:`~OpenID.try_login`.
The responses of these extensions are available during the :meth:`after_login`
function, as entries in resp.extensions.

Full Example
------------

To see the full code of that example, you can download the code `from
github <http://github.com/mitsuhiko/flask-openid>`_.

Changes
-------

1.2
```

-   The safe_roots argument and URL security system was added.

-   The OpenID extensions system was added.

1.0
```

-   the OpenID object is not registered to an application which allows
    configuration values to be used and is also consistent with other
    Flask extensions.

API References
--------------

The full API reference:

.. autoclass:: OpenID
   :members:

.. autoclass:: OpenIDResponse
   :members:

.. data:: COMMON_PROVIDERS

   a dictionary of common provider name -> login URL mappings.  This can
   be used to implement "click button to login" functionality.

   Currently contains general purpose entrypoints for the following
   providers: ``google``, ``yahoo``, ``aol``, and ``steam``.

.. _Flask: http://flask.pocoo.org/
.. _OpenID: http://openid.net/
.. _python-openid: http://openidenabled.com/python-openid/
