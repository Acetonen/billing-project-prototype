# The Billing project prototype.

*The purpose of this project is to experiment with Service Layer architecture and Repository pattern in Django. And 
find the ways to easily migrate all project logic to another ORM web framework if we need.*

**Requirements:**
```
1) Each client in the system has one "wallet" containing money.
2) The information about a purse and the balance of funds on it is stored.
3) Clients can make money transfers to each other.
4) The information about all transactions in the client's purse is stored.
5) The project is an HTTP API that contains the main operations on
"wallets":
    1) creating a client with a purse;
    2) crediting funds to the client's purse;
    3) transfer of funds from one purse to another.
```

## Project Structure

- You can look at all ATD specifications of the project here `project/core/abstract_data_types.py`
- All use cases (businesses logic) you can find in `project/[app_name]/use_cases.py`
- ORM Repository realisation `project/core/repos.py`

## Database Schema.

![](docs/final_base_schema.png)

## Project Architecture.

The architecture of the project was created with *Repository* and *Service Layer* patterns in mind.

**Service Layer** gives to us the purpose to separate all business logic as "use cases" in a separate module as Interactors. 
(ex: *project/payments/use_cases*). We can maintain all business logic in one place and reuse popular use cases.

**Repository** pattern chose in future purpose to switch to another ORM or raw SQL easily. We can add to our interactors 
constructors methods (def \_\_init__()) in the future and chose different repo to depend on business needs. 
We also don't use any ModelSerializers, only plain Serializer. Views also almost clean from ORM code.

## Start Up.

You can easily start up the project with:
```
docker-compose up
```
When the project will starts. You can go to the swagger page 
(this is also the main page in the project for easy debug in the current prototype project state) 
here: [localhost](http://localhost)
Then you can register user with swagger:
![](docs/registration.png)
For test purposes user creates with is_staff permissions, so you can login with django admin and has access to all api 
methods in swagger:
![](docs/login.png)

## Tests.

You can run test with
```
docker-compose exec web python -m pytest
```
The core bottleneck of such financial projects is a Race condition, we handle it in the main Transaction interactor:
project.payments.use_cases.MakeTransferInteractor
We lock sender table with **SELECT ... FOR UPDATE** (*select_for_update()* in ORM) and **UPDATE** (*F('balance') + sum* in ORM) to 
handle such effect. The worst thing that can be happing is net lag occurs during a transaction, two transactions make 
simultaneously and the user has a minus in his wallet. To test such a case we use *aiohttp* library and asynchronous 
test + lag emulation in logic. You can check it here:
```
project/payments/tests/test_race_condition_in_transaction.py
```

*MIT License*