const express = require('express');
const router = express.Router();
const autodesk = require('../services/autodesk');
const multer = require('multer');
const path = require('path');

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, path.join(__dirname, '../uploads'))
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + '-' + file.originalname)
    }
});
const upload = multer({ storage: storage });

// Get Forge token
router.get('/token', async (req, res) => {
    try {
        const token = await autodesk.getViewerToken();
        res.json(token);
    } catch (error) {
        console.error('Token error:', error);
        res.status(500).json({ error: 'Failed to get token' });
    }
});

// Upload and translate model
router.post('/models/upload', upload.single('model'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        // Create bucket if it doesn't exist
        await autodesk.createBucket();

        // Upload the model
        const uploadResponse = await autodesk.uploadModel(req.file.path);

        // Translate the model
        const translateResponse = await autodesk.translateModel(req.file.originalname);

        res.json({
            upload: uploadResponse,
            translation: translateResponse
        });
    } catch (error) {
        console.error('Upload/translate error:', error);
        res.status(500).json({ error: 'Failed to process model' });
    }
});

// Get latest model by type
router.get('/models/:type/latest', async (req, res) => {
    const modelTypes = {
        'inventor': '.iam',
        'twinmotion': '.fbx',
        'max': '.max',
        'revit': '.rvt'
    };

    const type = req.params.type;
    const extension = modelTypes[type] || '.rvt';
    try {
        // Get the latest model of the specified type from the uploads directory
        const uploadsDir = path.join(__dirname, '../uploads');
        const files = await fs.readdir(uploadsDir);
        const modelFiles = files.filter(f => f.endsWith(extension));
        
        if (modelFiles.length === 0) {
            return res.status(404).json({ error: `No ${type} models found` });
        }
        
        // Get the most recently modified file
        const latestModel = modelFiles.reduce((latest, current) => {
            const currentStat = fs.statSync(path.join(uploadsDir, current));
            const latestStat = fs.statSync(path.join(uploadsDir, latest));
            return currentStat.mtime > latestStat.mtime ? current : latest;
        });
        const urn = Buffer.from(`urn:adsk.objects:os.object:${process.env.FORGE_BUCKET_KEY}/${latestModel}`).toString('base64');
        res.json({ urn });
    } catch (error) {
        console.error('Model fetch error:', error);
        res.status(500).json({ error: 'Failed to get model' });
    }
});

module.exports = router;
