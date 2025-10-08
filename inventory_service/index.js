// Load environment variables from .env file at the very start
require('dotenv').config();

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 8000;

// --- Middleware ---
app.use(cors());
app.use(express.json()); // To parse JSON request bodies

// --- MongoDB Connection ---
const mongoUri = process.env.MONGO_URI;
if (!mongoUri) {
    console.error("FATAL ERROR: MONGO_URI is not defined.");
    process.exit(1);
}
mongoose.connect(mongoUri)
    .then(() => console.log("MongoDB connected successfully."))
    .catch(err => {
        console.error("MongoDB connection error:", err)
        // In a real app, you might want to exit if the DB connection fails
        // process.exit(1);
    });

// --- MongoDB Schema and Model for Inventory Items ---
const itemSchema = new mongoose.Schema({
    name: { type: String, required: true },
    quantity: { type: Number, required: true, default: 0 },
    owner_id: { type: Number, required: true, index: true }, // Index for fast user-based queries
});
const Item = mongoose.model('Item', itemSchema);

// --- JWT Authentication Middleware (The Security Guard) ---
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token == null) {
        return res.status(401).json({ error: "Authorization token is required" });
    }

    jwt.verify(token, process.env.JWT_SIGNING_KEY, (err, payload) => {
        if (err) {
            return res.status(403).json({ error: "Token is invalid or has expired" });
        }
        // If token is valid, attach the payload to the request and proceed
        req.user = payload;
        next();
    });
};

// --- API Routes (The CRUD Endpoints) ---

// Health check endpoint
app.get('/', (req, res) => {
    res.status(200).json({ message: 'Inventory service is running' });
});

// CREATE a new item
app.post('/items', authenticateToken, async (req, res) => {
    try {
        const newItem = new Item({
            name: req.body.name,
            quantity: req.body.quantity,
            owner_id: req.user.user_id, // Get the user ID from the JWT payload
        });
        await newItem.save();
        res.status(201).json(newItem);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// READ all items for the authenticated user
app.get('/items', authenticateToken, async (req, res) => {
    try {
        const items = await Item.find({ owner_id: req.user.user_id });
        res.status(200).json(items);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// UPDATE an item by ID
app.put('/items/:id', authenticateToken, async (req, res) => {
    try {
        const item = await Item.findOneAndUpdate(
            { _id: req.params.id, owner_id: req.user.user_id }, // Ensure user owns the item
            { name: req.body.name, quantity: req.body.quantity },
            { new: true, runValidators: true } // Return the updated document
        );
        if (!item) {
            return res.status(404).json({ error: 'Item not found or you do not have permission to edit it.' });
        }
        res.status(200).json(item);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// DELETE an item by ID
app.delete('/items/:id', authenticateToken, async (req, res) => {
    try {
        const item = await Item.findOneAndDelete({ _id: req.params.id, owner_id: req.user.user_id });
        if (!item) {
            return res.status(404).json({ error: 'Item not found or you do not have permission to delete it.' });
        }
        res.status(204).send(); // No content on successful deletion
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// --- Start the Server ---
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Inventory service listening on http://0.0.0.0:${PORT}`);
});