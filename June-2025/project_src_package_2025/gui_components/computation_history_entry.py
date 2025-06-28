import datetime


class ComputationRecord:
    def __init__(self, comp_type, params, mfpt=None, duration=None, csv_files=None, png_files=None):
        self.comp_type = comp_type
        self.params = params
        self.mfpt = mfpt
        self.duration = duration
        self.csv_files = csv_files
        self.png_files = png_files
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def display_name(self):
        return f"{self.comp_type} - {self.timestamp}"

    def to_dict(self):

        return {

            "comp_type": self.comp_type,
            "params": self.params,
            "mfpt": self.mfpt,
            "duration": self.duration,
            "csv_files": self.csv_files,
            "png_files": self.png_files,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(d):
        return ComputationRecord(
            d["comp_type"], d["params"],
            mfpt=d.get("mfpt"),
            duration=d.get("duration"),
            csv_files=d.get("csv_files"),
            png_files=d.get("png_files")
        )

