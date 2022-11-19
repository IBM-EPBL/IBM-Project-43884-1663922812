const table = document.getElementById("transaction");
const Name = document.getElementById("Name");
const Total = document.getElementById("balance");
const Amount = document.getElementById("Amount");
const AddExpense = document.querySelector("Button");
const moneyPlus = document.getElementById("money-plus");
const moneyMinus = document.getElementById("money-minus");
const inputerrName = document.getElementById("inputerrName");
const inputerrAmount = document.getElementById("inputerrAmount");

let navbar = document.querySelector(".dd_main");
navbar.addEventListener("click", function () {
  this.classList.toggle("active");
});
window.onload = () => {
  Name.value = "";
  Amount.value = "";
};

let transactions = [];

let removeTransaction = (id) => {
  transactions = transactions.filter((item) => {
    return item["id"] != id;
  });
  yourBalance();
  displayTransaction();
};

AddExpense.addEventListener("click", () => {
  addTransaction();
});

let addTransaction = () => {
  if (Name.value.trim() === "" || Amount.value.trim() === "") {
    alert("please add text and amount");
  } else {
    const transaction = {
      id: generateID(),
      name: Name.value,
      date: currentDate(),
      amount: parseInt(Amount.value),
    };

    transactions.push(transaction);
    yourBalance();
    displayTransaction();
    Name.value = "";
    Amount.value = "";
  }
};

// Generate random ID
let generateID = () => {
  return Math.floor(Math.random() * 100000000);
};

// current DATE
let currentDate = () => {
  const date = new Date();
  let currentDate = `${date.getDate()}-${
    date.getMonth() + 1
  }-${date.getFullYear()}`;
  return currentDate;
};

let displayTransaction = () => {
  let Data = "";
  const result = transactions.map((item) => {
    Data += `<li>
    ${item["name"]}
    <div>
      
      <button type="button" class="${
        Number(item["amount"]) > 0 ? "btn btn-success" : "btn btn-danger"
      } ">$${Math.abs(Number(item["amount"]))} </button>
      <span id="remove" onclick="removeTransaction( ${
        item["id"]
      } ) " class="icon-bin icon"  > </span>
      
    </div>
  </li> `;
  });

  table.innerHTML = Data;
};

let yourBalance = () => {
  const amounts = transactions.map((amount) => {
    return amount["amount"];
  });

  const total = amounts.reduce((acc, item) => (acc += item), 0).toFixed(2);

  const income = amounts
    .filter((item) => {
      return item > 0;
    })
    .reduce((acc, item) => (acc += item), 0)
    .toFixed(2);

  const expense = amounts
    .filter((item) => {
      return item < 0;
    })
    .reduce((acc, item) => (acc += item), 0)
    .toFixed(2);

  moneyPlus.innerText = `+${income}`;
  moneyMinus.innerText = `${expense}`;
  Total.innerText = `$${total}`;
};
