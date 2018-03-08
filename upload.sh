sudo rm -r breeder_blanket_model_maker.egg-info
sudo rm -r dist 
sudo rm -r build 
rm -r .pytest_cache

git add .
git commit -m 'fixed pip install'
git push

python setup.py sdist
# python setup.py bdist_wheel --universal
# test the distributions
twine upload dist/*

