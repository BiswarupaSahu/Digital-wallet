# Digital-wallet
Digital Wallet Backend API Flowchart

1. User Registration & Authentication
   - User sends registration data
   - System hashes password and stores user
   - User authenticates via HTTP Basic Auth

2. Wallet Operations
   - Fund Account
     * User sends fund amount
     * System credits user balance
     * Creates credit transaction record
   - Pay User
     * User sends recipient and amount
     * System checks balance and recipient
     * Debits sender, credits recipient
     * Creates debit and credit transaction records
   - Check Balance
     * User requests balance (optional currency)
     * System returns balance with conversion if needed

3. Transaction History
   - User requests transaction statement
   - System returns list of transactions ordered by timestamp

4. Product Catalog
   - Add Product
     * Admin/user adds product details
     * System stores product in catalog
   - List Products
     * User requests product list
     * System returns all products

5. Purchase Product
   - User sends product ID to buy
   - System checks user balance and product availability
   - Debits user balance by product price
   - Creates debit transaction and purchase record

Entities:
- User
- Transaction
- Product
- Purchase

Relationships:
- User has many Transactions (sent and received)
- User has many Purchases
- Purchase links User, Product, and Transaction

This flowchart outlines the main API flows and data relationships.
