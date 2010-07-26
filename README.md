SecInv
======
SecInv consists of a Django backend, a simple XML-RPC server, and
an XML-RPC client.

# Dependencies

* Apache 2 w/ mod_python (or similar)
* MySQL 5 (or similar)

# Dependencies Installed via pip

* MySQLdb-1.2.3c1 (must be 1.2.1p2 or newer)
* Django 1.2
* django-reversion 1.3.1
* pygments 1.3.1


# Installing Packages on Ubuntu
If you're running a recent version of Ubuntu, you can [install the required
dependencies automatically](apt:python-dev,python-virtualenv,libmysqlclient-dev).
Otherwise, the following command will install the required dependencies:

<pre>
sudo aptitude install python-dev python-virtualenv libmysqlclient-dev
</pre>

# Installing Packages on Mac OS X

First, download and install [Homebrew](http://github.com/mxcl/homebrew), then
[Xcode](http://developer.apple.com/technologies/xcode.html).
Finally, you should install these following packages:

<pre>
brew install python mysql git
</pre>

# MySQL

Initialize your MySQL environment using the following command:

<pre>
mysql_install_db
</pre>

Then follow the instructions to start the MySQL daemon.

Log in using `mysql -u root -p`, and create a database:

<pre>
> CREATE DATABASE secinv;
> exit;
</pre>

# Virtualenv

Using `easy_install`, grab `virtualenv` so we can create an isolated Python
environment for development:

<pre>
sudo easy_install virtualenv
</pre>

# Virtualenvwrapper 

Get `virtualenvwrapper` so we can easily activate and deactivate virtual
environments from the shell.

<pre>
curl http://bitbucket.org/dhellmann/virtualenvwrapper/raw/f31869779141/virtualenvwrapper_bashrc -o ~/.virtualenvwrapper
mkdir ~/.virtualenvs
</pre>

And, add this to your ~/.bashrc:

<pre>
export WORKON_HOME=$HOME/.virtualenvs
source $HOME/.virtualenvwrapper
</pre>

Finally, `exec bash`.

# Mac OS X Virtualenv

Designate a directory to keep your projects. I prefer `~/Sites/virtualenvs`.

<pre>
mkdir ~/Sites/virtualenvs
cd ~/Sites/virtualenvs
</pre>

Use `git` to grab the latest copy of the development branch:

<pre>
mkvirtualenv --no-site-packages secinv
git clone git://github.com/cvan/secinv.git --branch server_side
cd secinv/
</pre>

Now let's use `pip` to conveniently download and install all the remaining
dependencies:

<pre>
pip install -r requirements.txt
</pre>

# Django

Change directories to the Django root project directory.

<pre>
cd secinv/
</pre>

Modify the `settings.py` file as you see fit (namely, the `BASE_PATH` and
database credentials).

Sync the Django database models (and set up the Django admin authentication):

<pre>
python manage.py syncdb
</pre>

Any time you want to run the development server:

<pre>
python manage.py runserver
</pre>
