# Week 2 Self-check

## 1. Why does POST /tasks return 201 instead of 200?

Because POST /tasks is used to create a new task.

So when the task is created successfully, we return 201, which means that a new resource was created.

200 also means the request was successful, but 201 is more specific when something new has been created.

## 2. What is the difference between 404 and 422?

404 means that the thing we are looking for does not exist.

422 means that the data sent by the user is not valid or does not match the expected type or structure.
(FastAPI validates the data before sending it to the endpoint function)

## 3. Why do we use exclude_unset=True?

Because when we use PATCH, we only want to change the fields that the user actually sent.

## 4. What is the problem with in-memory storage?

The problem is that the tasks are stored only in the application's memory, If we restart or stop the application, the data inside tasks will be lost.

## 5. Why are TaskCreate and Task separate models?

Because the data that the user sends is not the same as the complete task.

TaskCreate represents the data that the user provides when creating a task.

Task represents the complete task, including the id that is created by the server.